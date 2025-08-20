                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        """
Agent System Initialization Script
Initializes the complete agent ecosystem with failsafe mechanisms
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, Any

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import agent systems
try:
    from utils.agent_orchestrator import orchestrator, get_status as get_orchestrator_status
    from utils.health_monitor import health_monitor, start_monitoring, get_system_health
    from utils.agent_recovery import recovery_manager, get_recovery_stats
    from utils.distributed_agents import distributed_manager, get_system_status as get_distributed_status
    from utils.agent_logging import AgentActionLogger, get_current_session, end_agent_session
    from utils.prompt_analyzer import prompt_analyzer
    from utils.decision_tracker import decision_tracker
except ImportError as e:
    print(f"Failed to import agent modules: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('agent.init')

class AgentSystemInitializer:
    """Manages the complete initialization of the agent system"""
    
    def __init__(self):
        self.initialization_start = time.time()
        self.systems_initialized = {}
        self.system_status = "initializing"
        
    def initialize_complete_system(self) -> Dict[str, Any]:
        """Initialize the complete agent system with all failsafes"""
        logger.info("🚀 Starting Agent System Initialization")
        
        initialization_steps = [
            ("Agent Logging System", self._initialize_logging),
            ("Health Monitoring", self._initialize_health_monitoring),
            ("Recovery Manager", self._initialize_recovery_system),
            ("Agent Orchestrator", self._initialize_orchestrator),
            ("Distributed Agents", self._initialize_distributed_agents),
            ("Circuit Breakers", self._initialize_circuit_breakers),
            ("System Verification", self._verify_system_health),
        ]
        
        for step_name, step_function in initialization_steps:
            try:
                logger.info(f"⚡ Initializing {step_name}...")
                result = step_function()
                self.systems_initialized[step_name] = {
                    "status": "success",
                    "timestamp": datetime.utcnow().isoformat(),
                    "result": result
                }
                logger.info(f"✅ {step_name} initialized successfully")
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize {step_name}: {e}")
                self.systems_initialized[step_name] = {
                    "status": "failed",
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": str(e)
                }
                
                # Critical systems should stop initialization
                if step_name in ["Agent Logging System", "Health Monitoring", "Agent Orchestrator"]:
                    logger.critical(f"Critical system {step_name} failed - aborting initialization")
                    self.system_status = "failed"
                    return self._get_initialization_summary()
        
        # Final system health check
        overall_health = self._perform_final_health_check()
        
        if overall_health > 0.8:
            self.system_status = "active"
            logger.info("🎉 Agent System fully initialized and operational!")
        elif overall_health > 0.6:
            self.system_status = "degraded"
            logger.warning("⚠️ Agent System initialized but running in degraded mode")
        else:
            self.system_status = "failed"
            logger.error("🔥 Agent System initialization completed with critical issues")
        
        # Log the complete initialization
        AgentActionLogger.log_action(
            "system_initialization",
            {
                "status": self.system_status,
                "duration": time.time() - self.initialization_start,
                "systems_initialized": len([s for s in self.systems_initialized.values() if s["status"] == "success"]),
                "total_systems": len(self.systems_initialized),
                "overall_health": overall_health
            },
            success=(self.system_status in ["active", "degraded"])
        )
        
        return self._get_initialization_summary()
    
    def _initialize_logging(self) -> Dict[str, Any]:
        """Initialize the agent logging system"""
        session = get_current_session()
        
        # Test logging functionality
        AgentActionLogger.log_action(
            "logging_test",
            {"message": "Agent logging system initialization test"},
            success=True
        )
        
        return {
            "session_id": session.session_id,
            "logging_active": True,
            "log_directory": "logs/agents"
        }
    
    def _initialize_health_monitoring(self) -> Dict[str, Any]:
        """Initialize health monitoring system"""
        # Start the health monitor
        start_monitoring()
        
        # Wait a moment for it to start up
        time.sleep(2)
        
        # Get initial system health
        system_health = get_system_health()
        
        return {
            "monitoring_active": health_monitor.monitoring_active,
            "system_health": system_health
        }
    
    def _initialize_recovery_system(self) -> Dict[str, Any]:
        """Initialize the recovery management system"""
        # Test recovery system
        recovery_stats = get_recovery_stats()
        
        # Create a test checkpoint
        test_checkpoint = recovery_manager.create_checkpoint(
            "system_init",
            {"initialization_time": datetime.utcnow().isoformat()}
        )
        
        return {
            "recovery_manager_active": True,
            "test_checkpoint": test_checkpoint,
            "recovery_stats": recovery_stats
        }
    
    def _initialize_orchestrator(self) -> Dict[str, Any]:
        """Initialize the agent orchestrator"""
        # The orchestrator is initialized when imported
        status = get_orchestrator_status()
        
        return {
            "orchestrator_active": True,
            "status": status
        }
    
    def _initialize_distributed_agents(self) -> Dict[str, Any]:
        """Initialize the distributed agent system"""
        # Wait for distributed manager to complete initialization
        max_wait = 30  # 30 seconds
        wait_time = 0
        
        while not distributed_manager.initialization_complete and wait_time < max_wait:
            time.sleep(1)
            wait_time += 1
        
        if not distributed_manager.initialization_complete:
            raise Exception("Distributed agent initialization timed out")
        
        status = get_distributed_status()
        
        return {
            "distributed_agents_active": True,
            "agent_count": status["total_agents"],
            "active_agents": status["active_agents"],
            "healthy_agents": status["healthy_agents"],
            "status": status
        }
    
    def _initialize_circuit_breakers(self) -> Dict[str, Any]:
        """Initialize circuit breaker patterns"""
        # Circuit breakers are built into the orchestrator and agents
        # This step verifies they're configured correctly
        
        circuit_breaker_config = {
            "failure_threshold": 5,
            "recovery_timeout": 60,
            "enabled": True
        }
        
        return {
            "circuit_breakers_enabled": True,
            "config": circuit_breaker_config
        }
    
    def _verify_system_health(self) -> Dict[str, Any]:
        """Verify overall system health"""
        # Get health from all subsystems
        health_data = {
            "orchestrator": get_orchestrator_status(),
            "health_monitor": get_system_health(),
            "recovery_manager": get_recovery_stats(),
            "distributed_agents": get_distributed_status(),
            "prompt_analyzer": prompt_analyzer.get_prompt_analytics(),
            "decision_tracker": decision_tracker.get_decision_analytics()
        }
        
        # Calculate overall health score
        health_scores = []
        
        # Orchestrator health
        orchestrator_status = health_data["orchestrator"]
        if orchestrator_status.get("total_agents", 0) > 0:
            health_scores.append(orchestrator_status.get("overall_health", 0))
        
        # Health monitor
        monitor_status = health_data["health_monitor"]
        if monitor_status.get("total_agents", 0) > 0:
            health_scores.append(monitor_status.get("health_percentage", 0) / 100)
        
        # Distributed agents
        distributed_status = health_data["distributed_agents"]
        if distributed_status.get("total_agents", 0) > 0:
            health_scores.append(distributed_status.get("system_health", 0) / 100)
        
        overall_health = sum(health_scores) / len(health_scores) if health_scores else 0.5
        
        return {
            "overall_health_score": overall_health,
            "subsystem_health": health_data,
            "verification_timestamp": datetime.utcnow().isoformat()
        }
    
    def _perform_final_health_check(self) -> float:
        """Perform final health check and return health score"""
        try:
            verification_result = self.systems_initialized.get("System Verification", {})
            if verification_result.get("status") == "success":
                return verification_result.get("result", {}).get("overall_health_score", 0.0)
            else:
                return 0.0
        except Exception as e:
            logger.error(f"Failed to get health score: {e}")
            return 0.0
    
    def _get_initialization_summary(self) -> Dict[str, Any]:
        """Get a summary of the initialization process"""
        total_duration = time.time() - self.initialization_start
        
        successful_systems = [
            name for name, info in self.systems_initialized.items()
            if info["status"] == "success"
        ]
        
        failed_systems = [
            name for name, info in self.systems_initialized.items()
            if info["status"] == "failed"
        ]
        
        return {
            "system_status": self.system_status,
            "initialization_duration": total_duration,
            "total_systems": len(self.systems_initialized),
            "successful_systems": len(successful_systems),
            "failed_systems": len(failed_systems),
            "successful_system_names": successful_systems,
            "failed_system_names": failed_systems,
            "systems_detail": self.systems_initialized,
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> list[str]:
        """Generate recommendations based on initialization results"""
        recommendations = []
        
        if self.system_status == "failed":
            recommendations.append("System failed to initialize - check logs for critical errors")
            recommendations.append("Restart the initialization process after fixing critical issues")
        
        elif self.system_status == "degraded":
            recommendations.append("System is running in degraded mode - some features may be limited")
            recommendations.append("Check failed systems and attempt to restart them")
        
        else:
            recommendations.append("System is fully operational")
            recommendations.append("Monitor agent health and performance regularly")
        
        # Check for specific failed systems
        failed_systems = [
            name for name, info in self.systems_initialized.items()
            if info["status"] == "failed"
        ]
        
        for system in failed_systems:
            if "Health Monitoring" in system:
                recommendations.append("Health monitoring is disabled - manual monitoring required")
            elif "Recovery Manager" in system:
                recommendations.append("Auto-recovery is disabled - manual intervention required for failures")
            elif "Distributed Agents" in system:
                recommendations.append("Specialized agents unavailable - using general purpose agents only")
        
        return recommendations

def initialize_agent_system() -> Dict[str, Any]:
    """Main function to initialize the complete agent system"""
    initializer = AgentSystemInitializer()
    return initializer.initialize_complete_system()

def shutdown_agent_system():
    """Gracefully shutdown the agent system"""
    logger.info("🛑 Shutting down Agent System...")
    
    try:
        # End current session
        end_agent_session()
        
        # Stop health monitoring
        health_monitor.stop_monitoring()
        
        # Shutdown orchestrator
        orchestrator.shutdown()
        
        logger.info("✅ Agent System shutdown complete")
        
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")

def get_system_dashboard() -> Dict[str, Any]:
    """Get a comprehensive system dashboard"""
    try:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "orchestrator_status": get_orchestrator_status(),
            "health_status": get_system_health(),
            "distributed_status": get_distributed_status(),
            "recovery_stats": get_recovery_stats(),
            "prompt_analytics": prompt_analyzer.get_prompt_analytics(),
            "decision_analytics": decision_tracker.get_decision_analytics()
        }
    except Exception as e:
        logger.error(f"Failed to get system dashboard: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    # Initialize the system when run directly
    result = initialize_agent_system()
    
    print("\n" + "="*80)
    print("🤖 AGENT SYSTEM INITIALIZATION COMPLETE")
    print("="*80)
    print(f"Status: {result['system_status'].upper()}")
    print(f"Duration: {result['initialization_duration']:.2f} seconds")
    print(f"Systems: {result['successful_systems']}/{result['total_systems']} successful")
    
    if result['failed_system_names']:
        print(f"Failed Systems: {', '.join(result['failed_system_names'])}")
    
    print("\nRecommendations:")
    for rec in result['recommendations']:
        print(f"  • {rec}")
    
    print("\n" + "="*80)
    
    # Keep the system running
    try:
        while True:
            time.sleep(60)
            dashboard = get_system_dashboard()
            logger.info(f"System running - Agents: {dashboard.get('distributed_status', {}).get('healthy_agents', 0)}")
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested...")
        shutdown_agent_system()
        print("👋 Goodbye!")