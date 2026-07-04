import json
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.routing import APIRoute
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User  # ⚡ Import the User model directly from your schema definitions

class AuditLogRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_handler = super().get_route_handler()

        async def custom_handler(request: Request) -> Response:
            # 1. Skip auditing completely for read-only GET requests
            if request.method == "GET":
                return await original_handler(request)

            # Check if request state has db context, otherwise spin up a standalone session
            has_state_db = hasattr(request.state, "db") and request.state.db is not None
            db: Session = request.state.db if has_state_db else SessionLocal()
            
            # 2. Safe request body stream caching pipeline
            input_data = None
            if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
                try:
                    body_bytes = await request.body()
                    if body_bytes:
                        input_data = json.loads(body_bytes.decode("utf-8"))
                        if "password" in input_data:
                            input_data["password"] = "********"
                    
                    # Reset stream pointer state so downstream Pydantic schemas can read it natively
                    async def receive():
                        return {"type": "http.request", "body": body_bytes, "more_body": False}
                    request._receive = receive
                except Exception:
                    pass

            # 3. Clean dynamic path parameters out of structural action strings
            path_segments = [s for s in request.url.path.split("/") if s]
            if path_segments:
                last_segment = path_segments[-1]
                if len(last_segment) > 20 or any(char.isdigit() for char in last_segment) or "-" in last_segment:
                    event_verb = path_segments[-2] if len(path_segments) > 1 else "ACTION"
                    action_name = f"{request.method}_{event_verb}".upper()
                else:
                    action_name = f"{request.method}_{last_segment}".upper()
            else:
                action_name = f"{request.method}_ACTION"

            # 4. Core request execution lifecycle
            try:
                response: Response = await original_handler(request)
                
                output_data = None
                if hasattr(response, "body"):
                    try:
                        output_data = json.loads(response.body.decode("utf-8"))
                    except Exception:
                        pass

                # 5. 🟢 DYNAMIC IDENTIFICATION & SIGNUP DATA FETCHING PIPELINE
                db_user_name = None
                db_user_email = None
                db_user_role = None  # 🟢 Start as None so we don't accidentally force a false role
                user_id_str = None

                # A. Direct read optimization out of request state wrapper
                if hasattr(request.state, "user") and request.state.user:
                    user_obj = request.state.user
                    user_id_str = str(getattr(user_obj, "id", ""))
                    db_user_name = getattr(user_obj, "name", None)
                    db_user_email = getattr(user_obj, "email", None)
                    db_user_role = getattr(user_obj, "role", None)

                # B. DEEP JWT SECURITY RECOVERY GAP GATE: Hard table queries via real authentication utility
                if not db_user_name:
                    auth_header = request.headers.get("Authorization")
                    if auth_header and auth_header.startswith("Bearer "):
                        try:
                            token = auth_header.split(" ")[1]
                            from app.services.user_auth_service import authenticate_user
                            
                            # Directly fetch the complete User model instance straight from the database
                            matched_user = authenticate_user(db=db, token=token)
                            
                            if matched_user:
                                user_id_str = str(matched_user.id)
                                db_user_name = matched_user.name  
                                db_user_email = matched_user.email
                                # 🟢 Dynamically query the actual user profile role, fallback to OPERATOR safely if missing
                                db_user_role = getattr(matched_user, "role", "OPERATOR")
                        except Exception:
                            pass

                # C. Final string fallback logic parsing parameters out of output metrics
                if not db_user_name and output_data and "controlled_by" in output_data:
                    db_user_email = output_data.get("controlled_by")
                    db_user_name = db_user_email.split("@")[0].capitalize()
                    
                # 🟢 Step 3: Ultimate safe row baseline definition. No hardcoded ADMIN overrides anymore!
                if not db_user_role:
                    db_user_role = "OPERATOR"

                workspace_id = request.headers.get("workspace-id")
                if not workspace_id and input_data:
                    workspace_id = input_data.get("workspace_id")
                if not workspace_id:
                    workspace_id = "UNKNOWN_WORKSPACE"

                # 6. Dispatch transaction row write permanently to DB
                from app.models.audit_log import AuditLog
                new_log = AuditLog(
                    workspace_id=str(workspace_id),
                    action=action_name,
                    user_id=user_id_str,
                    user_name=db_user_name or "System Operator",
                    user_email=db_user_email or "operator@agentpulse.ai",
                    user_role=str(db_user_role).upper(),
                    input_data=input_data,
                    output_data=output_data,
                    error_message=None  
                )
                db.add(new_log)
                db.commit()

                return response

            except Exception as exc:
                # Failure tracing block
                error_msg = str(exc)
                if isinstance(exc, HTTPException):
                    error_msg = f"HTTP {exc.status_code}: {exc.detail}"

                workspace_id = request.headers.get("workspace-id") or "UNKNOWN_WORKSPACE"
                
                from app.models.audit_log import AuditLog
                fail_log = AuditLog(
                    workspace_id=str(workspace_id),
                    action=action_name,
                    user_name="System Operator",
                    user_email="operator@agentpulse.ai",
                    user_role="OPERATOR",
                    input_data=input_data,
                    error_message=error_msg  
                )
                db.add(fail_log)
                db.commit()
                raise exc
            finally:
                if not has_state_db:
                    db.close()

        return custom_handler