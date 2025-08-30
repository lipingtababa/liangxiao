"""
TypeScript agent client for legacy system integration during migration.

Provides interface to communicate with the existing TypeScript single-agent
system while migration is in progress.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional, List
import aiohttp
import subprocess
from pathlib import Path

from models.github import IssueEvent

logger = logging.getLogger(__name__)


@dataclass
class TypeScriptResponse:
    """Response from TypeScript agent system."""
    success: bool
    workflow_id: Optional[str]
    message: str
    duration_seconds: float
    timestamp: datetime
    error_details: Optional[Dict[str, Any]] = None
    processing_log: Optional[List[str]] = None


class TypeScriptAgentClient:
    """
    Client for interfacing with the legacy TypeScript agent system.
    
    Provides methods to:
    - Submit issues for processing
    - Check processing status
    - Retrieve results
    - Monitor performance
    - Handle errors gracefully
    """
    
    def __init__(
        self,
        typescript_service_url: Optional[str] = None,
        timeout_seconds: int = 300,
        max_retries: int = 3
    ):
        """
        Initialize TypeScript client.
        
        Args:
            typescript_service_url: URL of TypeScript service (if remote)
            timeout_seconds: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.service_url = typescript_service_url or "http://localhost:3000"
        self.timeout = timeout_seconds
        self.max_retries = max_retries
        
        # Assume TypeScript system is local for now
        self.is_local = typescript_service_url is None
        
        # Path to TypeScript project (adjust as needed)
        self.typescript_path = Path("/path/to/typescript/agent")  # TODO: Configure this
    
    async def process_issue(self, event: IssueEvent) -> TypeScriptResponse:
        """
        Submit issue to TypeScript system for processing.
        
        Args:
            event: GitHub issue event to process
            
        Returns:
            Response containing processing results and metrics
        """
        start_time = datetime.now()
        
        try:
            logger.info(
                f"Submitting issue #{event.issue.number} to TypeScript system: "
                f"{event.issue.title}"
            )
            
            if self.is_local:
                result = await self._process_local_typescript(event)
            else:
                result = await self._process_remote_typescript(event)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return TypeScriptResponse(
                success=result.get("success", False),
                workflow_id=result.get("workflow_id"),
                message=result.get("message", "Processing completed"),
                duration_seconds=duration,
                timestamp=datetime.now(),
                error_details=result.get("error_details"),
                processing_log=result.get("processing_log", [])
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Failed to process issue with TypeScript system: {e}")
            
            return TypeScriptResponse(
                success=False,
                workflow_id=None,
                message=f"TypeScript processing failed: {str(e)}",
                duration_seconds=duration,
                timestamp=datetime.now(),
                error_details={"exception": str(e), "type": type(e).__name__}
            )
    
    async def _process_local_typescript(self, event: IssueEvent) -> Dict[str, Any]:
        """
        Process issue using local TypeScript system.
        
        This method assumes the TypeScript system can be invoked as a 
        command-line tool or Node.js script.
        """
        try:
            # Prepare issue data for TypeScript system
            issue_data = {
                "action": event.action,
                "issue": {
                    "number": event.issue.number,
                    "title": event.issue.title,
                    "body": event.issue.body,
                    "labels": [label.name for label in event.issue.labels],
                    "assignees": [assignee.login for assignee in event.issue.assignees],
                    "state": event.issue.state,
                    "html_url": event.issue.html_url
                },
                "repository": {
                    "name": event.repository.name,
                    "full_name": event.repository.full_name,
                    "owner": event.repository.owner.login
                },
                "sender": {
                    "login": event.sender.login
                }
            }
            
            # Write issue data to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(issue_data, f, indent=2)
                temp_file = f.name
            
            try:
                # Execute TypeScript agent (adjust command as needed)
                # This is a placeholder - actual implementation depends on how
                # the TypeScript system is structured
                cmd = [
                    "node",
                    str(self.typescript_path / "index.js"),
                    "--input", temp_file,
                    "--format", "json"
                ]
                
                logger.info(f"Executing TypeScript agent: {' '.join(cmd)}")
                
                result = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=self.typescript_path
                )
                
                stdout, stderr = await asyncio.wait_for(
                    result.communicate(),
                    timeout=self.timeout
                )
                
                # Parse output
                if result.returncode == 0:
                    try:
                        output = json.loads(stdout.decode())
                        return {
                            "success": True,
                            "workflow_id": output.get("workflow_id", f"ts_{event.issue.number}"),
                            "message": output.get("message", "Processing completed"),
                            "processing_log": output.get("log", [])
                        }
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse TypeScript output as JSON: {e}")
                        return {
                            "success": True,
                            "workflow_id": f"ts_{event.issue.number}",
                            "message": "Processing completed (non-JSON output)",
                            "processing_log": [stdout.decode()]
                        }
                else:
                    error_msg = stderr.decode() if stderr else "Unknown error"
                    return {
                        "success": False,
                        "message": f"TypeScript agent failed: {error_msg}",
                        "error_details": {
                            "return_code": result.returncode,
                            "stderr": error_msg,
                            "stdout": stdout.decode() if stdout else ""
                        }
                    }
                    
            finally:
                # Clean up temporary file
                try:
                    Path(temp_file).unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete temporary file {temp_file}: {e}")
                    
        except asyncio.TimeoutError:
            logger.error(f"TypeScript processing timed out after {self.timeout}s")
            return {
                "success": False,
                "message": f"Processing timed out after {self.timeout} seconds",
                "error_details": {"timeout": True}
            }
        except Exception as e:
            logger.error(f"Error in local TypeScript processing: {e}")
            return {
                "success": False,
                "message": f"Local processing error: {str(e)}",
                "error_details": {"exception": str(e)}
            }
    
    async def _process_remote_typescript(self, event: IssueEvent) -> Dict[str, Any]:
        """
        Process issue using remote TypeScript service.
        
        This method communicates with the TypeScript system via HTTP API.
        """
        try:
            # Prepare payload for remote service
            payload = {
                "event_type": "issues",
                "action": event.action,
                "issue": {
                    "number": event.issue.number,
                    "title": event.issue.title,
                    "body": event.issue.body,
                    "labels": [{"name": label.name} for label in event.issue.labels],
                    "assignees": [{"login": assignee.login} for assignee in event.issue.assignees],
                    "state": event.issue.state,
                    "html_url": event.issue.html_url
                },
                "repository": {
                    "name": event.repository.name,
                    "full_name": event.repository.full_name,
                    "owner": {"login": event.repository.owner.login}
                },
                "sender": {
                    "login": event.sender.login
                }
            }
            
            # Send request to TypeScript service
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as session:
                
                url = f"{self.service_url}/webhook/github"
                headers = {
                    "Content-Type": "application/json",
                    "X-GitHub-Event": "issues"
                }
                
                logger.info(f"Sending request to TypeScript service: {url}")
                
                async with session.post(
                    url,
                    json=payload,
                    headers=headers
                ) as response:
                    
                    response_data = await response.text()
                    
                    if response.status == 200:
                        try:
                            result = json.loads(response_data)
                            return {
                                "success": True,
                                "workflow_id": result.get("workflow_id", f"ts_remote_{event.issue.number}"),
                                "message": result.get("message", "Processing completed"),
                                "processing_log": result.get("log", [])
                            }
                        except json.JSONDecodeError:
                            return {
                                "success": True,
                                "workflow_id": f"ts_remote_{event.issue.number}",
                                "message": "Processing completed",
                                "processing_log": [response_data]
                            }
                    else:
                        return {
                            "success": False,
                            "message": f"TypeScript service returned {response.status}",
                            "error_details": {
                                "status_code": response.status,
                                "response_body": response_data
                            }
                        }
                        
        except asyncio.TimeoutError:
            logger.error(f"Remote TypeScript request timed out after {self.timeout}s")
            return {
                "success": False,
                "message": f"Remote request timed out after {self.timeout} seconds",
                "error_details": {"timeout": True}
            }
        except Exception as e:
            logger.error(f"Error in remote TypeScript processing: {e}")
            return {
                "success": False,
                "message": f"Remote processing error: {str(e)}",
                "error_details": {"exception": str(e)}
            }
    
    async def check_health(self) -> Dict[str, Any]:
        """
        Check if TypeScript system is healthy and responsive.
        
        Returns:
            Health status information
        """
        try:
            start_time = datetime.now()
            
            if self.is_local:
                health = await self._check_local_health()
            else:
                health = await self._check_remote_health()
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "healthy": health.get("healthy", False),
                "response_time_seconds": duration,
                "details": health.get("details", {}),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _check_local_health(self) -> Dict[str, Any]:
        """Check health of local TypeScript system."""
        try:
            # Check if TypeScript files exist
            if not self.typescript_path.exists():
                return {
                    "healthy": False,
                    "details": {"error": f"TypeScript path not found: {self.typescript_path}"}
                }
            
            # Check if Node.js is available
            try:
                result = await asyncio.create_subprocess_exec(
                    "node", "--version",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await result.communicate()
                
                if result.returncode != 0:
                    return {
                        "healthy": False,
                        "details": {"error": "Node.js not available"}
                    }
                
                node_version = stdout.decode().strip()
                
                # Try to run a simple health check command
                health_cmd = [
                    "node", "-e", "console.log(JSON.stringify({status: 'ok', timestamp: new Date().toISOString()}))"
                ]
                
                result = await asyncio.create_subprocess_exec(
                    *health_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await asyncio.wait_for(result.communicate(), timeout=10)
                
                if result.returncode == 0:
                    return {
                        "healthy": True,
                        "details": {
                            "node_version": node_version,
                            "typescript_path": str(self.typescript_path)
                        }
                    }
                else:
                    return {
                        "healthy": False,
                        "details": {"error": f"Node.js execution failed: {stderr.decode()}"}
                    }
                    
            except Exception as e:
                return {
                    "healthy": False,
                    "details": {"error": f"Node.js check failed: {str(e)}"}
                }
                
        except Exception as e:
            return {
                "healthy": False,
                "details": {"error": str(e)}
            }
    
    async def _check_remote_health(self) -> Dict[str, Any]:
        """Check health of remote TypeScript service."""
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            ) as session:
                
                # Try health endpoint first
                health_url = f"{self.service_url}/health"
                
                try:
                    async with session.get(health_url) as response:
                        if response.status == 200:
                            health_data = await response.json()
                            return {
                                "healthy": True,
                                "details": health_data
                            }
                        else:
                            raise aiohttp.ClientResponseError(
                                None, None, status=response.status
                            )
                except (aiohttp.ClientResponseError, json.JSONDecodeError):
                    # Fall back to root endpoint
                    async with session.get(self.service_url) as response:
                        if response.status == 200:
                            return {
                                "healthy": True,
                                "details": {"status": "service_responding"}
                            }
                        else:
                            return {
                                "healthy": False,
                                "details": {"error": f"Service returned {response.status}"}
                            }
                            
        except Exception as e:
            return {
                "healthy": False,
                "details": {"error": str(e)}
            }
    
    async def get_processing_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get status of a workflow being processed by TypeScript system.
        
        Args:
            workflow_id: Identifier of the workflow to check
            
        Returns:
            Status information for the workflow
        """
        try:
            if self.is_local:
                # For local system, we'll simulate status checking
                # In reality, this would depend on how the TypeScript system
                # exposes workflow status
                return {
                    "workflow_id": workflow_id,
                    "status": "completed",  # Assume completed for now
                    "message": "Status checking not implemented for local TypeScript system"
                }
            else:
                # For remote system, query status endpoint
                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as session:
                    
                    status_url = f"{self.service_url}/workflow/{workflow_id}"
                    
                    async with session.get(status_url) as response:
                        if response.status == 200:
                            return await response.json()
                        elif response.status == 404:
                            return {
                                "workflow_id": workflow_id,
                                "status": "not_found",
                                "message": "Workflow not found in TypeScript system"
                            }
                        else:
                            return {
                                "workflow_id": workflow_id,
                                "status": "error",
                                "message": f"Status check failed: {response.status}"
                            }
                            
        except Exception as e:
            logger.error(f"Failed to get processing status for {workflow_id}: {e}")
            return {
                "workflow_id": workflow_id,
                "status": "error",
                "message": f"Status check error: {str(e)}"
            }