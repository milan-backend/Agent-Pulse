import json
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.routing import APIRoute
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.workspace_member import WorkspaceMember

class AuditLogRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_handler = super().get_route_handler()

        async def custom_handler(request: Request) -> Response:
            if request.method == "GET":
                return await original_handler(request)

            has_state_db = hasattr(request.state, "db") and request.state.db is not None
            db: Session = request.state.db if has_state_db else SessionLocal()
            
            input_data = None
            if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
                try:
                    body_bytes = await request.body()
                    if body_bytes:
                        input_data = json.loads(body_bytes.decode("utf-8"))
                        if "password" in input_data:
                            input_data["password"] = "********"
                    
                    async def receive():
                        return {"type": "http.request", "body": body_bytes, "more_body": False}
                    request._receive = receive
                except Exception:
                    pass

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

            workspace_id = request.headers.get("workspace-id")
            if not workspace_id and input_data:
                workspace_id = input_data.get("workspace_id")
            if not workspace_id:
                workspace_id = "UNKNOWN_WORKSPACE"

            def resolve_user_context():
                u_name, u_email, u_role, u_id = None, None, None, None
                
                if hasattr(request.state, "user") and request.state.user:
                    user_obj = request.state.user
                    u_id = str(getattr(user_obj, "id", ""))
                    u_name = getattr(user_obj, "name", None)
                    u_email = getattr(user_obj, "email", None)

                if not u_name:
                    auth_header = request.headers.get("Authorization")
                    if auth_header and auth_header.startswith("Bearer "):
                        try:
                            token = auth_header.split(" ")[1]
                            from app.services.user_auth_service import authenticate_user
                            matched_user = authenticate_user(db=db, token=token)
                            if matched_user:
                                u_id = str(matched_user.id)
                                u_name = matched_user.name  
                                u_email = matched_user.email
                        except Exception:
                            pass

                if u_id and workspace_id != "UNKNOWN_WORKSPACE" and db:
                    try:
                        member_record = db.query(WorkspaceMember).filter(
                            WorkspaceMember.workspace_id == workspace_id,
                            WorkspaceMember.user_id == u_id
                        ).first()
                        if member_record and member_record.role:
                            u_role = str(getattr(member_record.role, "value", member_record.role)).upper().strip()
                    except Exception:
                        pass

                if not u_role:
                    u_role = "OPERATOR"

                return u_id, u_name, u_email, u_role

            try:
                response: Response = await original_handler(request)
                
                output_data = None
                if hasattr(response, "body"):
                    try:
                        output_data = json.loads(response.body.decode("utf-8"))
                    except Exception:
                        pass

                user_id_str, db_user_name, db_user_email, db_user_role = resolve_user_context()

                if not db_user_name and output_data and "controlled_by" in output_data:
                    db_user_email = output_data.get("controlled_by")
                    db_user_name = db_user_email.split("@")[0].capitalize()

                from app.models.audit_log import AuditLog
                new_log = AuditLog(
                    workspace_id=str(workspace_id),
                    action=action_name,
                    user_id=user_id_str,
                    user_name=db_user_name or "System Operator",
                    user_email=db_user_email or "operator@agentpulse.ai",
                    user_role=str(db_user_role),
                    input_data=input_data,
                    output_data=output_data,
                    error_message=None  # 🟢 No error message means it was a success!
                )
                db.add(new_log)
                db.commit()

                return response

            except Exception as exc:
                error_msg = str(exc)
                if isinstance(exc, HTTPException):
                    error_msg = f"HTTP {exc.status_code}: {exc.detail}"

                user_id_str, db_user_name, db_user_email, db_user_role = resolve_user_context()

                from app.models.audit_log import AuditLog
                fail_log = AuditLog(
                    workspace_id=str(workspace_id),
                    action=action_name,
                    user_id=user_id_str,
                    user_name=db_user_name or "System Operator",
                    user_email=db_user_email or "operator@agentpulse.ai",
                    user_role=str(db_user_role),
                    input_data=input_data,
                    output_data=None,
                    error_message=error_msg  # 🟢 Storing the error trace natively tags it as a FAILURE
                )
                db.add(fail_log)
                db.commit()
                raise exc
            finally:
                if not has_state_db:
                    db.close()

        return custom_handler