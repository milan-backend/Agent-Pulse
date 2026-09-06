"use client";

import Link from "next/link";
import { 
  Cpu, Activity, ArrowLeft, Pause, Settings, KeyRound, FileText, Database, 
  Server, Lock, CheckCircle2, Copy, Plus, X, TerminalSquare
} from "lucide-react";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { toast } from "sonner";
import { databaseApi, DBConnectionPayload } from "@/components/api";

export default function AgentDatabasePage() {
  const params = useParams();
  const agentId = params?.agent_id as string;
  const router = useRouter();

  const [loading, setLoading] = useState(false);
  const [newTable, setNewTable] = useState("");
  
  const [payload, setPayload] = useState<DBConnectionPayload>({
    db_type: "postgresql",
    db_host: "",
    db_port: 5432,
    db_name: "",
    db_username: "agentpulse_ro",
    db_password: "",
    jwks_url: "",
    sync_all_tables: true,
    allowed_tables: []
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    if (name === "db_port") {
      setPayload(prev => ({ ...prev, [name]: parseInt(value) || 0 }));
    } else {
      setPayload(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleAddTable = (e: React.FormEvent) => {
    e.preventDefault();
    if (newTable.trim() && !payload.allowed_tables.includes(newTable.trim())) {
      setPayload(prev => ({ ...prev, allowed_tables: [...prev.allowed_tables, newTable.trim()] }));
      setNewTable("");
    }
  };

  const removeTable = (tableName: string) => {
    setPayload(prev => ({
      ...prev,
      allowed_tables: prev.allowed_tables.filter(t => t !== tableName)
    }));
  };

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!payload.sync_all_tables && payload.allowed_tables.length === 0) {
      toast.error("You must add at least one allowed table.");
      return;
    }

    try {
      setLoading(true);
      const workspaceId = localStorage.getItem("workspace_id");
      const response = await databaseApi.connectDatabase(workspaceId, payload);
      toast.success(response.message || "Database connected securely!");
      router.push(`/agent/${agentId}/monitor`);
    } catch (error: any) {
      toast.error(error.message || "Failed to connect to database");
    } finally {
      setLoading(false);
    }
  };

  // 🟢 DYNAMIC READ-ONLY SCRIPT GENERATOR (Password Masked)
  const getReadOnlyScript = () => {
    const db = payload.db_name || "[database_name]";
    const user = payload.db_username || "agentpulse_ro";
    
    // 🛡️ SECURITY PATCH: Never expose the plaintext password in the generated script window
    const pass = "********"; 

    if (payload.db_type === "postgresql") {
      let script = `-- 1. Create the read-only user (Replace stars with your password)\nCREATE ROLE ${user} WITH LOGIN PASSWORD '${pass}';\n\n`;
      script += `-- 2. Grant connection access\nGRANT CONNECT ON DATABASE ${db} TO ${user};\nGRANT USAGE ON SCHEMA public TO ${user};\n\n`;
      if (payload.sync_all_tables) {
        script += `-- 3. Grant access to ALL tables\nGRANT SELECT ON ALL TABLES IN SCHEMA public TO ${user};\nALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO ${user};`;
      } else {
        script += `-- 3. Grant access to SPECIFIC tables\n`;
        if (payload.allowed_tables.length === 0) script += `-- (Add tables in the form to generate grants)\n`;
        payload.allowed_tables.forEach(t => {
          script += `GRANT SELECT ON TABLE ${t} TO ${user};\n`;
        });
      }
      return script;
    } 
    
    if (payload.db_type === "mysql") {
      let script = `-- 1. Create the read-only user (Replace stars with your password)\nCREATE USER '${user}'@'%' IDENTIFIED BY '${pass}';\n\n`;
      if (payload.sync_all_tables) {
        script += `-- 2. Grant access to ALL tables\nGRANT SELECT ON ${db}.* TO '${user}'@'%';\n`;
      } else {
        script += `-- 2. Grant access to SPECIFIC tables\n`;
        if (payload.allowed_tables.length === 0) script += `-- (Add tables in the form to generate grants)\n`;
        payload.allowed_tables.forEach(t => {
          script += `GRANT SELECT ON ${db}.${t} TO '${user}'@'%';\n`;
        });
      }
      script += `\nFLUSH PRIVILEGES;`;
      return script;
    }

    if (payload.db_type === "mongodb") {
      return `// MongoDB uses JS shell commands\n\nuse ${db};\n\ndb.createUser({\n  user: "${user}",\n  pwd: "${pass}",\n  roles: [\n    { role: "read", db: "${db}" }\n  ]\n});`;
    }

    if (payload.db_type === "sqlserver") {
      let script = `-- 1. Create Login and User\nUSE [master];\nCREATE LOGIN [${user}] WITH PASSWORD = '${pass}';\n\nUSE [${db}];\nCREATE USER [${user}] FOR LOGIN [${user}];\n\n`;
      if (payload.sync_all_tables) {
        script += `-- 2. Grant read to ALL tables\nALTER ROLE db_datareader ADD MEMBER [${user}];`;
      } else {
        script += `-- 2. Grant read to SPECIFIC tables\n`;
        payload.allowed_tables.forEach(t => {
          script += `GRANT SELECT ON [${t}] TO [${user}];\n`;
        });
      }
      return script;
    }

    return `-- Script generation for ${payload.db_type} is not yet supported in this preview.`;
  };

  const copyScript = () => {
    navigator.clipboard.writeText(getReadOnlyScript());
    toast.success("Script copied to clipboard!");
  };

  return (
    <div className="h-screen w-screen bg-[#020817] text-white flex overflow-hidden select-none">
      
      {/* FIXED SIDEBAR */}
      <aside className="w-[300px] shrink-0 border-r border-cyan-500/10 bg-[#040b18] p-6 flex flex-col justify-between h-full sticky top-0 overflow-y-auto scrollbar-none">
        <div className="space-y-10">
          <div>
            <h1 className="text-5xl font-black">
              <span className="text-cyan-400">Agent</span>
              <span className="text-white">Pulse</span>
            </h1>
            <p className="mt-2 text-zinc-400 text-sm">Runtime Agent Control</p>
          </div>

          <div className="flex flex-col gap-3 group">  
            <Link href="/dashboard/agents" className="flex items-center gap-3 rounded-2xl bg-[#0b1628] border border-cyan-500/5 px-5 py-4 font-bold transition-all hover:bg-cyan-500/10">  
              <ArrowLeft size={18} className="text-zinc-400" /> 
              <span>Back To Agents</span>  
            </Link>  
            
            <Link href={`/agent/${agentId}/settings`} className="flex items-center gap-3 rounded-2xl bg-[#0b1628] border border-cyan-500/5 px-5 py-4 font-bold text-zinc-300 transition-all hover:text-cyan-300 hover:border-cyan-500/20 hover:bg-cyan-500/5">  
              <Settings size={18} className="text-zinc-500" /> 
              <span>Agent Settings</span>  
            </Link>  

            <Link href={`/agent/${agentId}/provider`} className="flex items-center gap-3 rounded-2xl bg-[#0b1628] border border-cyan-500/5 px-5 py-4 font-bold text-zinc-300 transition-all hover:text-cyan-300 hover:border-cyan-500/20 hover:bg-cyan-500/5">  
              <KeyRound size={18} className="text-zinc-500" /> 
              <span>API Provider</span>  
            </Link>  

            <Link href={`/agent/${agentId}/knowledge`} className="flex items-center gap-3 rounded-2xl bg-[#0b1628] border border-cyan-500/5 px-5 py-4 font-bold text-zinc-300 transition-all hover:text-emerald-400 hover:border-emerald-500/20 hover:bg-emerald-500/5">  
              <FileText size={18} className="text-zinc-500" /> 
              <span>Agent Knowledge</span>  
            </Link> 

            <div className="flex items-center gap-3 rounded-2xl bg-blue-500/10 border border-blue-500/20 px-5 py-4 font-bold text-blue-400 shadow-[0_0_15px_rgba(59,130,246,0.1)]">  
              <Database size={18} /> 
              <span>Live Database</span>  
            </div> 

            <Link href={`/agent/${agentId}/tasks`} className="flex items-center gap-3 rounded-2xl bg-[#0b1628] border border-cyan-500/5 px-5 py-4 font-bold text-zinc-300 transition-all hover:text-purple-300 hover:border-purple-500/20 hover:bg-purple-500/5">  
              <Activity size={18} className="text-zinc-500" /> 
              <span>Agent Tasks</span>  
            </Link>  

            <Link href={`/agent/${agentId}/monitor`} className="flex items-center gap-3 rounded-2xl bg-[#0b1628] border border-cyan-500/5 px-5 py-4 font-bold text-zinc-300 transition-all hover:text-cyan-400 hover:border-cyan-500/20 hover:bg-cyan-500/5">  
              <Cpu size={18} className="text-zinc-500 group-hover:text-cyan-400" /> 
              <span>Pipeline Monitor</span>  
            </Link> 
          </div>  
        </div>
      </aside>  

      {/* MAIN CONTAINER */}  
      <main className="flex-1 p-8 overflow-y-auto h-full flex flex-col min-w-0 bg-[#020817] scrollbar-thin scrollbar-thumb-zinc-900">  
        
        <div className="flex items-center justify-between gap-6 flex-wrap flex-shrink-0 w-full bg-[#08111f]/30 border border-blue-500/10 p-6 rounded-3xl shadow-[0_0_20px_rgba(59,130,246,0.03)]">  
          <div className="flex items-center gap-6 min-w-0">  
            <div className="h-24 w-24 rounded-3xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center shadow-[0_0_35px_rgba(59,130,246,0.15)] shrink-0">  
              <Database size={48} className="text-blue-400" />  
            </div>  
            <div className="min-w-0">  
              <h1 className="text-4xl md:text-5xl font-black tracking-tight text-white truncate max-w-full">Live SQL Engine</h1>  
              <p className="mt-2 text-zinc-400 text-lg font-medium">Connect external databases with zero-trust security</p>  
            </div>  
          </div>  
        </div>  

        <div className="mt-8 grid lg:grid-cols-2 gap-8">
          
          {/* LEFT: THE CONFIGURATION FORM */}
          <div className="rounded-3xl border border-cyan-500/10 bg-[#08111f] p-8 shadow-lg">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-3 text-zinc-100">
              <Server className="text-cyan-400" /> Connection Setup
            </h2>
            
            <form id="db-form" onSubmit={handleConnect} className="space-y-6">
              
              {/* 1. DATABASE TYPE & TABLE SCOPE */}
              <div className="space-y-6 pb-6 border-b border-cyan-500/10">
                <div className="space-y-2">
                  <label className="text-sm font-semibold text-zinc-400">Database Engine</label>
                  <select 
                    name="db_type" 
                    value={payload.db_type} 
                    onChange={handleInputChange}
                    className="w-full bg-[#040b18] border border-cyan-500/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-cyan-400/50 transition-colors cursor-pointer"
                  >
                    <option value="postgresql">PostgreSQL</option>
                    <option value="mysql">MySQL</option>
                    <option value="mongodb">MongoDB</option>
                    <option value="sqlserver">SQL Server</option>
                    <option value="snowflake">Snowflake</option>
                  </select>
                </div>

                {/* 🟢 NEW: Schema Access Radio Toggles */}
                <div className="space-y-4">
                  <h3 className="text-sm font-semibold text-zinc-400">Schema Access</h3>
                  
                  <div className="flex items-center gap-8">
                    {/* ALL TABLES RADIO */}
                    <label className="flex items-center gap-3 cursor-pointer group">
                      <div className="relative flex items-center justify-center">
                        <input 
                          type="radio" 
                          name="sync_all_tables"
                          checked={payload.sync_all_tables === true}
                          onChange={() => setPayload(prev => ({ ...prev, sync_all_tables: true }))}
                          className="sr-only" 
                        />
                        <div className={`w-5 h-5 rounded-full border transition-all ${payload.sync_all_tables ? 'border-[6px] border-cyan-500 bg-[#040b18]' : 'border-zinc-600 bg-transparent group-hover:border-cyan-500/50'}`}></div>
                      </div>
                      <span className="text-zinc-300 font-medium group-hover:text-white transition-colors">All tables</span>
                    </label>

                    {/* SELECTED TABLES RADIO */}
                    <label className="flex items-center gap-3 cursor-pointer group">
                      <div className="relative flex items-center justify-center">
                        <input 
                          type="radio" 
                          name="sync_all_tables"
                          checked={payload.sync_all_tables === false}
                          onChange={() => setPayload(prev => ({ ...prev, sync_all_tables: false }))}
                          className="sr-only" 
                        />
                        <div className={`w-5 h-5 rounded-full border transition-all ${!payload.sync_all_tables ? 'border-[6px] border-cyan-500 bg-[#040b18]' : 'border-zinc-600 bg-transparent group-hover:border-cyan-500/50'}`}></div>
                      </div>
                      <span className="text-zinc-300 font-medium group-hover:text-white transition-colors">Selected tables</span>
                    </label>
                  </div>

                  {/* SMART TABLE ADDER */}
                  {!payload.sync_all_tables && (
                    <div className="mt-4 animate-fade-in space-y-3 p-4 bg-[#040b18]/50 border border-cyan-500/10 rounded-xl">
                      <div className="flex gap-2">
                        <input 
                          type="text" 
                          value={newTable}
                          onChange={(e) => setNewTable(e.target.value)}
                          onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTable(e))}
                          placeholder="Enter exact table name..." 
                          className="flex-1 bg-[#040b18] border border-cyan-500/20 rounded-xl px-4 py-2 text-sm text-white focus:outline-none focus:border-cyan-400/50"
                        />
                        <button 
                          type="button"
                          onClick={handleAddTable}
                          className="bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 rounded-xl px-4 flex items-center gap-2 font-bold transition-all"
                        >
                          <Plus size={16} /> Add
                        </button>
                      </div>

                      <div className="flex flex-wrap gap-2 pt-2">
                        {payload.allowed_tables.length === 0 && (
                          <span className="text-xs text-zinc-500 italic">No tables selected yet.</span>
                        )}
                        {payload.allowed_tables.map(table => (
                          <div key={table} className="flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 text-blue-300 px-3 py-1.5 rounded-lg text-sm transition-all hover:bg-blue-500/20">
                            {table}
                            <button type="button" onClick={() => removeTable(table)} className="hover:text-red-400 transition-colors">
                              <X size={14} />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* 2. CONNECTION CREDENTIALS */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2 col-span-2">
                  <label className="text-sm font-semibold text-zinc-400">Database Name</label>
                  <input required type="text" name="db_name" value={payload.db_name} onChange={handleInputChange} placeholder="production_db" className="w-full bg-[#040b18] border border-cyan-500/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-cyan-400/50" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-semibold text-zinc-400">Host / IP</label>
                  <input required type="text" name="db_host" value={payload.db_host} onChange={handleInputChange} placeholder="db.mycompany.com" className="w-full bg-[#040b18] border border-cyan-500/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-cyan-400/50" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-semibold text-zinc-400">Port</label>
                  <input required type="number" name="db_port" value={payload.db_port} onChange={handleInputChange} placeholder="5432" className="w-full bg-[#040b18] border border-cyan-500/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-cyan-400/50" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-semibold text-zinc-400">Read-Only Username</label>
                  <input required type="text" name="db_username" value={payload.db_username} onChange={handleInputChange} placeholder="agentpulse_ro" className="w-full bg-[#040b18] border border-cyan-500/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-cyan-400/50" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-semibold text-zinc-400">Password</label>
                  <input required type="password" name="db_password" value={payload.db_password} onChange={handleInputChange} placeholder="••••••••••••" className="w-full bg-[#040b18] border border-cyan-500/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-cyan-400/50" />
                </div>
              </div>

              {/* 3. ZERO-TRUST GUARD */}
              <div className="space-y-2 pt-2 border-t border-cyan-500/10 pt-6">
                <label className="text-sm font-semibold text-zinc-400 flex items-center gap-2">
                  <Lock size={16} className="text-emerald-400" /> JWKS Identity URL
                </label>
                <input required type="url" name="jwks_url" value={payload.jwks_url} onChange={handleInputChange} placeholder="https://your-tenant.auth0.com/.well-known/jwks.json" className="w-full bg-[#040b18] border border-emerald-500/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-emerald-400/50" />
              </div>
            </form>
          </div>

          {/* RIGHT: LIVE SCRIPT GENERATOR & SUBMIT BUTTON */}
          <div className="flex flex-col gap-6">
            
            <div className="flex-1 rounded-3xl border border-blue-500/20 bg-[#08111f] p-6 shadow-lg flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold flex items-center gap-2 text-zinc-100">
                  <TerminalSquare size={20} className="text-blue-400" /> Auto-Generated Setup Script
                </h3>
                <button 
                  onClick={copyScript}
                  className="p-2 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 rounded-lg transition-colors border border-blue-500/20"
                  title="Copy to Clipboard"
                >
                  <Copy size={16} />
                </button>
              </div>
              
              <p className="text-sm text-zinc-400 mb-4 leading-relaxed">
                Run this securely in your database terminal to create the read-only user. For security, your password has been masked with <strong className="text-zinc-200">********</strong>. Be sure to replace it when executing!
              </p>

              <div className="flex-1 bg-[#040b18] border border-blue-500/10 rounded-2xl p-4 overflow-y-auto relative group max-h-[450px]">
                <pre className="text-sm text-blue-300 font-mono whitespace-pre-wrap leading-relaxed">
                  {getReadOnlyScript()}
                </pre>
              </div>
            </div>

            <button 
              form="db-form"
              type="submit" 
              disabled={loading}
              className="w-full rounded-2xl bg-cyan-500 py-5 font-black text-lg text-black hover:bg-cyan-400 transition-all shadow-[0_0_25px_rgba(34,211,238,0.25)] hover:shadow-[0_0_35px_rgba(34,211,238,0.4)] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? "Indexing Schema..." : (
                <>Connect & Index Schema <ArrowLeft className="rotate-180" size={20} /></>
              )}
            </button>
          </div>
        </div>

      </main>  
    </div>
  );
}