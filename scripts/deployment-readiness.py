#!/usr/bin/env python3
"""
Men's Circle Management Platform - Deployment Readiness Validator
Task 1.2.10: Test complete project structure deployment readiness
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime

def main():
    """Main deployment readiness validation."""
    print("🚀 Testing complete project structure deployment readiness...")
    
    project_root = Path(__file__).parent.parent
    start_time = time.perf_counter()
    
    checks = []
    
    # 1. Infrastructure checks
    print("🏗️  Checking deployment infrastructure...")
    workflows_dir = project_root / '.github' / 'workflows'
    required_workflows = ['ci.yml', 'test.yml', 'deploy.yml']
    
    for workflow in required_workflows:
        if (workflows_dir / workflow).exists():
            checks.append(f"✅ {workflow} workflow exists")
        else:
            checks.append(f"❌ {workflow} workflow missing")
    
    # 2. Docker infrastructure
    print("🐳 Checking containerization...")
    docker_dir = project_root / 'docker'
    if docker_dir.exists():
        checks.append("✅ Docker directory exists")
        
        dockerfiles = ['backend.Dockerfile', 'frontend.Dockerfile']
        for dockerfile in dockerfiles:
            if (docker_dir / dockerfile).exists():
                checks.append(f"✅ {dockerfile} exists")
            else:
                checks.append(f"❌ {dockerfile} missing")
        
        if (docker_dir / 'docker-compose.yml').exists():
            checks.append("✅ Docker Compose configuration exists")
        else:
            checks.append("❌ Docker Compose configuration missing")
    else:
        checks.append("❌ Docker directory missing")
    
    # 3. Security checks
    print("🔒 Checking security configuration...")
    if (project_root / '.env.example').exists():
        checks.append("✅ Environment example file exists")
    else:
        checks.append("❌ Environment example file missing")
    
    gitignore_path = project_root / '.gitignore'
    if gitignore_path.exists():
        gitignore_content = gitignore_path.read_text()
        if '.env' in gitignore_content:
            checks.append("✅ Environment files properly ignored")
        else:
            checks.append("❌ Environment files not properly ignored")
    
    # 4. Health check validation
    print("📊 Running project health check...")
    health_script = project_root / 'scripts' / 'health-check.py'
    if health_script.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(health_script), '--format', 'json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode in [0, 1]:
                health_report = json.loads(result.stdout)
                health_percentage = health_report['health_percentage']
                
                if health_percentage >= 80.0:
                    checks.append(f"✅ Project health: {health_percentage:.1f}% (deployment ready)")
                else:
                    checks.append(f"⚠️ Project health: {health_percentage:.1f}% (below deployment threshold)")
            else:
                checks.append("❌ Health check failed to execute")
        except Exception as e:
            checks.append(f"❌ Health check error: {str(e)}")
    else:
        checks.append("❌ Health check script missing")
    
    # Calculate results
    passed = len([check for check in checks if check.startswith('✅')])
    failed = len([check for check in checks if check.startswith('❌')])
    warnings = len([check for check in checks if check.startswith('⚠️')])
    total = len(checks)
    
    readiness_percentage = (passed / total) * 100
    execution_time = time.perf_counter() - start_time
    
    # Determine deployment readiness
    if readiness_percentage >= 90 and failed == 0:
        status = "READY"
        status_emoji = "✅"
    elif readiness_percentage >= 70:
        status = "WARNING"
        status_emoji = "⚠️"
    else:
        status = "NOT_READY"
        status_emoji = "❌"
    
    # Print results
    print(f"\n{'='*60}")
    print(f"🚀 DEPLOYMENT READINESS REPORT")
    print(f"{'='*60}")
    print(f"📊 Overall Status: {status_emoji} {status}")
    print(f"📈 Readiness Score: {readiness_percentage:.1f}%")
    print(f"⏱️  Execution Time: {execution_time:.2f}s")
    print(f"📋 Checks: {total} total (✅ {passed}, ❌ {failed}, ⚠️ {warnings})")
    
    print(f"\n📋 DETAILED RESULTS:")
    for check in checks:
        print(f"   {check}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if failed > 0:
        print("   🔧 Fix critical deployment issues before production deployment")
    if warnings > 0:
        print("   ⚡ Address warning issues for optimal deployment")
    if readiness_percentage >= 90:
        print("   🎉 Project is ready for deployment!")
    
    print(f"\n{'='*60}")
    print(f"Task 1.2.10 completed: Deployment readiness validated")
    print(f"Deployment Status: {status} ({readiness_percentage:.1f}%)")
    
    # Exit with appropriate code
    if status == "READY":
        return 0
    elif status == "WARNING":
        return 1
    else:
        return 2

if __name__ == '__main__':
    sys.exit(main()) 