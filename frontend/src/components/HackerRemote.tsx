import { useState } from 'react';
import { Skull, ShieldAlert, Zap, RadioTower } from 'lucide-react';
import { post } from '../services/api';

export function HackerRemote() {
  const [status, setStatus] = useState<string>('STANDBY');
  
  const launchCampaign = async () => {
    setStatus('LAUNCHING...');
    try {
      await post('/api/cyber/auto-defense/trigger-campaign');
      setStatus('CAMPAIGN ACTIVE');
      setTimeout(() => setStatus('STANDBY'), 3000);
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
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
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
        marginBottom: '40px',
        width: '100%',
        maxWidth: '300px',
        textAlign: 'center'
      }}>
        <span style={{ display: 'block', fontSize: '12px', color: '#ff8888', marginBottom: '5px' }}>UPLINK STATUS</span>
        <b style={{ fontSize: '18px', animation: status === 'STANDBY' ? 'none' : 'pulse 1s infinite' }}>{status}</b>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', width: '100%', maxWidth: '300px' }}>
        <button 
          onClick={launchCampaign}
          style={{
            backgroundColor: '#330000',
            border: '2px solid #ff3333',
            color: '#ff3333',
            padding: '20px',
            fontSize: '18px',
            fontWeight: 'bold',
            borderRadius: '8px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '10px',
            textTransform: 'uppercase'
          }}
        >
          <Zap size={24} />
          Inject Attack
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
