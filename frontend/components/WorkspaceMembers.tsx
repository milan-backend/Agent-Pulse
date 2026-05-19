"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  Shield,
  UserPlus,
  Users,
  Settings,
  Trash2,
} from "lucide-react";

interface WorkspaceMember {

  user_id: string;

  email: string;

  name: string;

  role: string;
}

export default function WorkspaceMemberPage() {

  const [members, setMembers] =
    useState<WorkspaceMember[]>([]);

  const [email, setEmail] =
    useState("");

  const [role, setRole] =
    useState("viewer");

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {

    loadMembers();

  }, []);

  // =========================
  // LOAD MEMBERS
  // =========================

  async function loadMembers() {

    try {

      const token =
        localStorage.getItem("token");

      const workspaceId =
        localStorage.getItem(
          "workspace_id"
        );

      console.log(
        "Workspace ID:",
        workspaceId
      );

      const response =
        await fetch(
          "http://127.0.0.1:8000/workspace/members",
          {
            method: "GET",

            headers: {

              Authorization:
                `Bearer ${token}`,

              "workspace-id":
                workspaceId || "",
            },
          }
        );

      const data =
        await response.json();

      if (!response.ok) {

        console.error(data);

        alert(
          data.detail ||
          "Failed to load members"
        );

        return;
      }

      setMembers(
        data.members || []
      );

    } catch (error) {

      console.error(error);

      alert(
        "Failed to load workspace"
      );

    } finally {

      setLoading(false);

    }
  }

  // =========================
  // ADD MEMBER
  // =========================

  async function addMember() {

    try {

      const token =
        localStorage.getItem("token");

      const workspaceId =
        localStorage.getItem(
          "workspace_id"
        );

      const response =
        await fetch(
          "http://127.0.0.1:8000/workspace/add-member",
          {
            method: "POST",

            headers: {

              "Content-Type":
                "application/json",

              Authorization:
                `Bearer ${token}`,

              "workspace-id":
                workspaceId || "",
            },

            body: JSON.stringify({
              email,
              role,
            }),
          }
        );

      const data =
        await response.json();

      if (!response.ok) {

        alert(
          data.detail ||
          "Failed to add member"
        );

        return;
      }

      alert(
        "Member added successfully"
      );

      setEmail("");

      setRole("viewer");

      loadMembers();

    } catch (error) {

      console.error(error);

      alert(
        "Something went wrong"
      );
    }
  }

  // =========================
  // UPDATE ROLE
  // =========================

  async function updateRole(
    memberEmail: string,
    newRole: string
  ) {

    try {

      const token =
        localStorage.getItem("token");

      const workspaceId =
        localStorage.getItem(
          "workspace_id"
        );

      const response =
        await fetch(
          `http://127.0.0.1:8000/workspace/members/role?email=${memberEmail}&role=${newRole}`,
          {
            method: "PATCH",

            headers: {

              Authorization:
                `Bearer ${token}`,

              "workspace-id":
                workspaceId || "",
            },
          }
        );

      const data =
        await response.json();

      if (!response.ok) {

        alert(
          data.detail ||
          "Failed to update role"
        );

        return;
      }

      alert(
        "Role updated successfully"
      );

      loadMembers();

    } catch (error) {

      console.error(error);

      alert(
        "Something went wrong"
      );
    }
  }

  // =========================
  // DELETE MEMBER
  // =========================

  async function deleteMember(
    userId: string
  ) {

    try {

      const token =
        localStorage.getItem("token");

      const workspaceId =
        localStorage.getItem(
          "workspace_id"
        );

      const response =
        await fetch(
          `http://127.0.0.1:8000/workspace/members/${userId}`,
          {
            method: "DELETE",

            headers: {

              Authorization:
                `Bearer ${token}`,

              "workspace-id":
                workspaceId || "",
            },
          }
        );

      const data =
        await response.json();

      if (!response.ok) {

        alert(
          data.detail ||
          "Failed to remove member"
        );

        return;
      }

      alert(
        "Member removed successfully"
      );

      loadMembers();

    } catch (error) {

      console.error(error);

      alert(
        "Something went wrong"
      );
    }
  }

  // =========================
  // LOADING
  // =========================

  if (loading) {

    return (

      <div
        className="
          min-h-screen
          bg-[#020817]
          text-white
          flex
          items-center
          justify-center
        "
      >

        Loading workspace...

      </div>
    );
  }

  // =========================
  // UI
  // =========================

  return (

    <div
      className="
        min-h-screen
        bg-[#020817]
        text-white
        p-8
      "
    >

      {/* HEADER */}

      <div
        className="
          flex
          items-center
          justify-between
          flex-wrap
          gap-6
        "
      >

        <div>

          <h1
            className="
              text-6xl
              font-black
              text-cyan-400
            "
          >

            Workspace

          </h1>

          <p
            className="
              mt-3
              text-zinc-400
              text-lg
            "
          >

            Manage team members and roles.

          </p>

        </div>

        <div
          className="
            rounded-3xl
            border
            border-cyan-500/20
            bg-cyan-500/10
            px-8
            py-5
          "
        >

          <div
            className="
              flex
              items-center
              gap-4
            "
          >

            <Users
              className="
                text-cyan-300
              "
            />

            <div>

              <p className="text-zinc-400">

                Team Members

              </p>

              <h2
                className="
                  text-4xl
                  font-black
                  text-cyan-300
                "
              >

                {members.length}

              </h2>

            </div>

          </div>

        </div>

      </div>

      {/* ADD MEMBER */}

      <div
        className="
          mt-10
          rounded-3xl
          border
          border-cyan-500/10
          bg-[#08111f]
          p-8
        "
      >

        <div
          className="
            flex
            items-center
            gap-4
          "
        >

          <UserPlus
            className="
              text-cyan-300
            "
          />

          <h2
            className="
              text-4xl
              font-black
            "
          >

            Add Workspace Member

          </h2>

        </div>

        <div
          className="
            mt-8
            grid
            grid-cols-1
            xl:grid-cols-3
            gap-6
          "
        >

          <input
            value={email}
            onChange={(e) =>
              setEmail(
                e.target.value
              )
            }
            placeholder="member@email.com"
            className="
              rounded-2xl
              bg-black
              border
              border-cyan-500/10
              p-5
              outline-none
            "
          />

          <select
            value={role}
            onChange={(e) =>
              setRole(
                e.target.value
              )
            }
            className="
              rounded-2xl
              bg-black
              border
              border-cyan-500/10
              p-5
              outline-none
            "
          >

            <option value="viewer">
              Viewer
            </option>

            <option value="operator">
              Operator
            </option>

            <option value="admin">
              Admin
            </option>

          </select>

          <button
            onClick={addMember}
            className="
              rounded-2xl
              bg-cyan-400
              text-black
              font-black
              transition-all
              hover:bg-cyan-300
            "
          >

            Add Member

          </button>

        </div>

      </div>

      {/* MEMBERS */}

      <div
        className="
          mt-10
          grid
          grid-cols-1
          xl:grid-cols-2
          gap-6
        "
      >

        {members.map((member, index) => (

          <div
            key={index}
            className="
              rounded-3xl
              border
              border-cyan-500/10
              bg-[#08111f]
              p-8
            "
          >

            <div
              className="
                flex
                items-start
                justify-between
                gap-6
                flex-wrap
              "
            >

              <div>

                <p className="text-zinc-400">

                  Workspace Member

                </p>

                <h2
                  className="
                    mt-3
                    text-2xl
                    font-black
                    break-all
                    text-cyan-300
                  "
                >

                  {member.email}

                </h2>

                <p
                  className="
                    mt-2
                    text-zinc-500
                  "
                >

                  {member.name}

                </p>

                <div
                  className="
                    mt-5
                    inline-flex
                    items-center
                    gap-2
                    rounded-2xl
                    border
                    border-cyan-500/20
                    bg-cyan-500/10
                    px-4
                    py-2
                  "
                >

                  <Shield
                    size={16}
                    className="text-cyan-300"
                  />

                  <span
                    className="
                      font-bold
                      capitalize
                    "
                  >

                    {member.role}

                  </span>

                </div>

              </div>

              <div
                className="
                  flex
                  items-center
                  gap-3
                  flex-wrap
                "
              >

                <select
                  value={member.role}
                  onChange={(e) =>
                    updateRole(
                      member.email,
                      e.target.value
                    )
                  }
                  className="
                    rounded-2xl
                    bg-black
                    border
                    border-cyan-500/10
                    px-5
                    py-4
                    outline-none
                  "
                >

                  <option value="viewer">
                    Viewer
                  </option>

                  <option value="operator">
                    Operator
                  </option>

                  <option value="admin">
                    Admin
                  </option>

                </select>

                <button
                  onClick={() =>
                    deleteMember(
                      member.user_id
                    )
                  }
                  className="
                    h-14
                    px-5
                    rounded-2xl
                    bg-red-500/20
                    border
                    border-red-500/20
                    text-red-300
                    hover:bg-red-500/30
                    flex
                    items-center
                    justify-center
                  "
                >

                  <Trash2 size={18} />

                </button>

                <div
                  className="
                    h-14
                    w-14
                    rounded-2xl
                    border
                    border-cyan-500/20
                    bg-cyan-500/10
                    flex
                    items-center
                    justify-center
                  "
                >

                  <Settings
                    className="
                      text-cyan-300
                    "
                  />

                </div>

              </div>

            </div>

          </div>

        ))}

      </div>

    </div>
  );
}