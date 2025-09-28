"""
WebSocket Manager for Real-time Communication
Manages WebSocket connections and broadcasts
"""

import json
import logging
from typing import List, Dict, Any
from enum import Enum
from datetime import datetime
from fastapi import WebSocket


logger = logging.getLogger(__name__)


def enum_serializer(obj):
    """Custom serializer for enum objects and other types"""
    if isinstance(obj, Enum):
        return obj.value
    elif isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)


class WebSocketManager:
    """Manages WebSocket connections and real-time broadcasting"""
    
    def __init__(self):
        # Store active connections
        self.active_connections: List[WebSocket] = []
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        
    async def connect(self, websocket: WebSocket, client_info: Dict[str, Any] = None):
        """Accept and store a WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Store connection metadata
        if client_info:
            self.connection_metadata[websocket] = client_info
        else:
            self.connection_metadata[websocket] = {
                "connected_at": websocket.client.host if websocket.client else "unknown",
                "client_id": f"client_{len(self.active_connections)}"
            }
            
        logger.info(f"WebSocket connection established. Total connections: {len(self.active_connections)}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection",
            "status": "connected",
            "client_id": self.connection_metadata[websocket]["client_id"],
            "message": "Connected to FinancePulse real-time stream"
        }, websocket)
        
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
        if websocket in self.connection_metadata:
            client_info = self.connection_metadata.pop(websocket)
            logger.info(f"WebSocket disconnected: {client_info.get('client_id', 'unknown')}")
            
        logger.info(f"WebSocket connection closed. Total connections: {len(self.active_connections)}")
        
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            if websocket in self.active_connections:
                await websocket.send_text(json.dumps(message, default=enum_serializer))
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
            self.disconnect(websocket)
            
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients"""
        if not self.active_connections:
            return
            
        message_text = json.dumps(message, default=enum_serializer)
        disconnected_clients = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_text)
            except Exception as e:
                logger.error(f"Failed to send message to client: {e}")
                disconnected_clients.append(connection)
                
        # Clean up disconnected clients
        for connection in disconnected_clients:
            self.disconnect(connection)
            
        if disconnected_clients:
            logger.info(f"Removed {len(disconnected_clients)} disconnected clients")
            
    async def broadcast_to_subset(self, message: Dict[str, Any], client_ids: List[str]):
        """Broadcast message to specific clients by ID"""
        message_text = json.dumps(message, default=enum_serializer)
        
        for connection, metadata in self.connection_metadata.items():
            if metadata.get("client_id") in client_ids:
                try:
                    await connection.send_text(message_text)
                except Exception as e:
                    logger.error(f"Failed to send message to client {metadata.get('client_id')}: {e}")
                    self.disconnect(connection)
                    
    def get_connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)
        
    def get_connection_info(self) -> List[Dict[str, Any]]:
        """Get information about all active connections"""
        return [
            {
                "client_id": metadata.get("client_id", "unknown"),
                "connected_at": metadata.get("connected_at", "unknown"),
                "status": "active"
            }
            for metadata in self.connection_metadata.values()
        ]