import docker
import json
from typing import Optional, List, Dict
from pathlib import Path

class DockerRunnerService:
    """Simple Docker container runner for quick container management."""
    
    def __init__(self, storage_file: str = "docker_containers.json"):
        self.client = docker.from_env()
        self.storage_file = storage_file
        self.container_id: Optional[str] = None
        self.containers = self._load_containers()
    
    def _load_containers(self) -> Dict[str, str]:
        """Load saved container IDs from file."""
        try:
            if Path(self.storage_file).exists():
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _save_containers(self) -> None:
        """Save container IDs to file."""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.containers, f, indent=2)
        except Exception:
            pass
    
    def _parse_additional_flags(self, flags: List[str]) -> Dict[str, any]:
        """Parse additional Docker flags into SDK parameters."""
        parsed = {
            'cap_add': [],
            'devices': [],
            'privileged': False,
            'network_mode': None,
            'restart_policy': None,
            'other_kwargs': {}
        }
        
        i = 0
        while i < len(flags):
            flag = flags[i]
            
            if flag == "--cap-add" and i + 1 < len(flags):
                parsed['cap_add'].append(flags[i + 1])
                i += 2
            elif flag == "--device" and i + 1 < len(flags):
                parsed['devices'].append(flags[i + 1])
                i += 2
            elif flag == "--privileged":
                parsed['privileged'] = True
                i += 1
            elif flag == "--network" and i + 1 < len(flags):
                parsed['network_mode'] = flags[i + 1]
                i += 2
            elif flag == "--restart" and i + 1 < len(flags):
                restart_value = flags[i + 1]
                if restart_value in ["no", "on-failure", "always", "unless-stopped"]:
                    parsed['restart_policy'] = {"Name": restart_value}
                i += 2
            else:
                # Handle other flags that might not have direct SDK equivalents
                i += 1
        
        return parsed
    
    def run(self, image: str, container_name: Optional[str] = None, 
            port_map: Optional[str] = None, 
            env_vars: Optional[Dict[str, str]] = None,
            volume_map: Dict[str, str] = None, 
            additional_flags: Optional[List[str]] = None) -> str:
        """
        Run a Docker container and save its ID.
        
        Args:
            image: Docker image name
            container_name: Optional container name for identification
            port_map: Port mapping (e.g., "8881:8881")
            env_vars: Environment variables as dict
            volume_map: Volume mapping (e.g., "./provider/spark:/etc/wireguard")
            additional_flags: Additional Docker flags
            
        Returns:
            Container ID
        """
        # Parse port mapping
        ports = {}
        if port_map:
            host_port, container_port = port_map.split(':')
            ports[f"{container_port}/tcp"] = host_port
        
        # Parse volume mapping
        volumes = {}
        if volume_map:
            host_path, container_path = volume_map.popitem()
            volumes[host_path] = {'bind': container_path, 'mode': 'rw'}
        
        # Parse additional flags
        flag_params = {}
        if additional_flags:
            parsed_flags = self._parse_additional_flags(additional_flags)
            flag_params.update({
                'cap_add': parsed_flags['cap_add'] or None,
                'devices': parsed_flags['devices'] or None,
                'privileged': parsed_flags['privileged'],
                'network_mode': parsed_flags['network_mode']
            })
            if parsed_flags['restart_policy']:
                flag_params['restart_policy'] = parsed_flags['restart_policy']
            # Remove None values
            flag_params = {k: v for k, v in flag_params.items() if v is not None and v != []}
        
        try:
            # Run the container
            container = self.client.containers.run(
                image=image,
                name=container_name,
                ports=ports,
                environment=env_vars or {},
                volumes=volumes,
                cap_add=["NET_ADMIN", "SYS_MODULE"],
                detach=True,
                **flag_params
            )
            
            self.container_id = container.id
            
            # Save container ID with name or image as key
            key = container_name or image
            self.containers[key] = self.container_id
            self._save_containers()
            
            return self.container_id
            
        except docker.errors.APIError as e:
            raise RuntimeError(f"Failed to run container: {e}")
    
    def stop_and_remove(self, container_key: Optional[str] = None) -> bool:
        """
        Stop and remove container.
        
        Args:
            container_key: Container name/image key (uses last run if None)
            
        Returns:
            True if successful
        """
        if container_key:
            target_id = self.containers.get(container_key)
        else:
            target_id = self.container_id
        
        if not target_id:
            return False
        
        try:
            container = self.client.containers.get(target_id)
            container.stop()
            container.remove()
            
            # Remove from storage
            if container_key and container_key in self.containers:
                del self.containers[container_key]
                self._save_containers()
            
            return True
        except docker.errors.NotFound:
            # Container already removed
            if container_key and container_key in self.containers:
                del self.containers[container_key]
                self._save_containers()
            return True
        except docker.errors.APIError:
            return False
    
    def cleanup_all(self) -> int:
        """
        Stop and remove all saved containers.
        
        Returns:
            Number of containers cleaned up
        """
        cleaned = 0
        for key in list(self.containers.keys()):
            if self.stop_and_remove(key):
                cleaned += 1
        return cleaned
    
    def list_saved_containers(self) -> Dict[str, str]:
        """Get all saved container IDs."""
        return self.containers.copy()
    
    def is_container_running(self, container_key: str) -> bool:
        """Check if a saved container is still running."""
        container_id = self.containers.get(container_key)
        if not container_id:
            return False
        
        try:
            container = self.client.containers.get(container_id)
            container.reload()  # Refresh container status
            return container.status == 'running'
        except docker.errors.NotFound:
            # Container no longer exists
            return False
        except docker.errors.APIError:
            return False
    
    def get_container_logs(self, container_key: str, tail: int = 100) -> str:
        """Get logs from a saved container."""
        container_id = self.containers.get(container_key)
        if not container_id:
            return ""
        
        try:
            container = self.client.containers.get(container_id)
            return container.logs(tail=tail).decode('utf-8')
        except docker.errors.NotFound:
            return ""
        except docker.errors.APIError:
            return ""
    
    def get_container_status(self, container_key: str) -> str:
        """Get status of a saved container."""
        container_id = self.containers.get(container_key)
        if not container_id:
            return "not_found"
        
        try:
            container = self.client.containers.get(container_id)
            container.reload()
            return container.status
        except docker.errors.NotFound:
            return "not_found"
        except docker.errors.APIError:
            return "error"