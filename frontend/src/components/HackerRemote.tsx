import { useState } from 'react';
import { Skull, ShieldAlert, Zap, ServerCrash, Database, Bug } from 'lucide-react';
import { post } from '../services/api';

export function HackerRemote() {
  const [status, setStatus] = useState<string>('STANDBY');
  
  const launchCampaign = async (scenario?: string) => {
    setStatus('LAUNCHING...');
    try {
      await post('/api/cyber/auto-defense/trigger-campaign', scenario ? { scenario } : {});
      setStatus('CAMPAIGN ACTIVE');
      setTimeout(() => setStatus('STANDBY'), 60000);
    } catch (e: any) {
      setStatus(`ERROR: ${e.message}`);
    }
  };

  const triggerDefense = async () => {
    setStatus('MITIGATING...');
    try {
      await post('/api/cyber/auto-defense/trigger-defense');
      setStatus('THREAT MITIGATED');
      setTimeout(() => setStatus('STANDBY'), 3000);
    } catch (e: any) {
      setStatus(`ERROR: ${e.message}`);
    }
  };

  const attackBtnStyle = {
    backgroundColor: '#330000',
    border: '2px solid #ff3333',
    color: '#ff3333',
    padding: '15px',
    fontSize: '16px',
    fontWeight: 'bold',
    borderRadius: '8px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '10px',
    textTransform: 'uppercase' as const
  };

  return (
    <div style={{
      backgroundColor: '#0a0a0a', 
      color: '#ff3333', 
      minHeight: '100vh', 
      padding: '20px',
      fontFamily: 'monospace',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <div style={{ textAlign: 'center', marginBottom: '30px' }}>
        <Skull size={48} color="#ff3333" style={{ marginBottom: '10px' }} />
        <h1 style={{ fontSize: '24px', margin: 0, textTransform: 'uppercase', letterSpacing: '2px' }}>
          Red Team Remote
        </h1>
        <p style={{ color: '#888', marginTop: '10px' }}>TARGET: NEXORA DIGITAL TWIN</p>
      </div>
      
      <div style={{
        backgroundColor: '#1a0000',
        border: '1px solid #ff3333',
        padding: '15px',
        borderRadius: '5px',
        marginBottom: '30px',
        width: '100%',
        maxWidth: '300px',
        textAlign: 'center'
      }}>
        <span style={{ display: 'block', fontSize: '12px', color: '#ff8888', marginBottom: '5px' }}>UPLINK STATUS</span>
        <b style={{ fontSize: '18px', animation: status === 'STANDBY' ? 'none' : 'pulse 1s infinite' }}>{status}</b>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', width: '100%', maxWidth: '300px' }}>
        <div style={{ fontSize: '12px', color: '#ff8888', textTransform: 'uppercase', textAlign: 'center', marginBottom: '-5px' }}>Payload Select</div>
        
        <button onClick={() => launchCampaign('OT_DISRUPTION')} style={attackBtnStyle}>
          <ServerCrash size={20} />
          Inject DDoS (OT)
        </button>

        <button onClick={() => launchCampaign('DATABASE_EXFILTRATION')} style={attackBtnStyle}>
          <Database size={20} />
          SQL Injection
        </button>

        <button onClick={() => launchCampaign('RANSOMWARE_IMPACT')} style={attackBtnStyle}>
          <Bug size={20} />
          Deploy Malware
        </button>

        <button onClick={() => launchCampaign()} style={{...attackBtnStyle, backgroundColor: '#220000', borderStyle: 'dashed'}}>
          <Zap size={20} />
          Random APT Attack
        </button>

        <button 
          onClick={triggerDefense}
          style={{
            backgroundColor: '#002233',
            border: '2px solid #33ccff',
            color: '#33ccff',
            padding: '20px',
            fontSize: '18px',
            fontWeight: 'bold',
            borderRadius: '8px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '10px',
            textTransform: 'uppercase',
            marginTop: '20px'
          }}
        >
          <ShieldAlert size={24} />
          Trigger SOAR
        </button>
      </div>

      <style>
        {`
          @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
          }
        `}
      </style>
    </div>
  );
}
