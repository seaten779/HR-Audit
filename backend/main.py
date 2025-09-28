#!/usr/bin/env python3
"""
HR Audit Backend - AI-Powered HR Analytics Engine
Main FastAPI application with WebSocket streaming and HR data analysis
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.routes import router as api_router
from app.services.transaction_simulator import TransactionSimulator
from app.services.websocket_manager import WebSocketManager
from app.services.anomaly_detector import AnomalyDetector
from app.services.explanation_engine import ExplanationEngine
from app.services.notification_service import notification_orchestrator
from app.services.twilio_phone_service import enhanced_phone_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global service instances
websocket_manager = WebSocketManager()
transaction_simulator = TransactionSimulator()
anomaly_detector = AnomalyDetector()
explanation_engine = ExplanationEngine()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 HR Audit backend starting up...")
    
    # Initialize services
    await anomaly_detector.initialize()
    logger.info("📊 Anomaly detector initialized")
    
    # Initialize notification system
    await notification_orchestrator.initialize()
    logger.info("🔔 Notification system initialized")
    
    # Initialize enhanced phone service
    await enhanced_phone_service.initialize()
    logger.info("📞 Enhanced phone service initialized")
    
    # Start background transaction simulation
    asyncio.create_task(transaction_stream_worker())
    logger.info("💳 Transaction simulation started")
    
    yield
    
    # Shutdown
    logger.info("🛑 HR Audit backend shutting down...")

app = FastAPI(
    title="HR Audit API",
    description="AI-Powered HR Analytics and Audit System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "HR Audit API",
        "version": "1.0.0",
        "description": "AI-Powered HR Analytics and Audit System",
        "status": "running",
        "docs": "/docs",
        "websocket": "/ws"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time(),
        "services": {
            "websocket_manager": "running",
            "transaction_simulator": "running",
            "anomaly_detector": "ready",
            "explanation_engine": "ready",
            "notification_orchestrator": "ready" if notification_orchestrator.is_initialized else "failed"
        }
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time data streaming"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            logger.info(f"Received WebSocket message: {data}")
            
            # Echo back for now (can be extended for client commands)
            await websocket.send_text(f"Echo: {data}")
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")

async def transaction_stream_worker():
    """Background worker that simulates transaction stream and processes anomalies"""
    logger.info("🔄 Starting transaction stream worker...")
    logger.info("📊 Anomaly injection configured: every 20-30 transactions")
    
    stats_counter = 0
    
    while True:
        try:
            # Generate a new transaction
            transaction = await transaction_simulator.generate_transaction()
            
            # Detect anomalies
            anomaly_result = await anomaly_detector.detect_anomaly(transaction)
            
            # Generate explanation if anomaly detected
            if anomaly_result.is_anomaly:
                explanation = await explanation_engine.generate_explanation(
                    transaction, anomaly_result
                )
                anomaly_result.explanation = explanation
                
                # Process notifications for anomalies
                if settings.ENABLE_NOTIFICATIONS:
                    try:
                        notification_results = await notification_orchestrator.process_anomaly_notification(
                            transaction, anomaly_result
                        )
                        if any(notification_results.values()):
                            logger.info(f"📲 Notifications sent for transaction {transaction.id}: {notification_results}")
                    except Exception as notification_error:
                        logger.error(f"Error processing notifications: {notification_error}")
            
            # Prepare message for broadcasting
            try:
                message = {
                    "type": "transaction",
                    "data": {
                        "transaction": transaction.model_dump(),
                        "anomaly": anomaly_result.model_dump() if anomaly_result.is_anomaly else None
                    },
                    "timestamp": transaction.timestamp.isoformat()
                }
            except Exception as serialization_error:
                logger.error(f"Error serializing transaction data: {serialization_error}")
                logger.error(f"Transaction merchant_category: {transaction.merchant_category}")
                logger.error(f"Transaction type: {transaction.type}")
                raise
            
            # Broadcast to all connected WebSocket clients
            await websocket_manager.broadcast(message)
            
            # Log anomaly statistics every 50 transactions
            stats_counter += 1
            if stats_counter % 50 == 0:
                anomaly_stats = transaction_simulator.get_anomaly_stats()
                logger.info(f"📊 Stats Update: {anomaly_stats['total_transactions']} transactions, {anomaly_stats['anomalous_transactions']} anomalies ({anomaly_stats['anomaly_rate_percent']}%), next anomaly in {anomaly_stats['next_anomaly_in']} transactions")
            
            # Wait before next transaction (adjustable rate)
            await asyncio.sleep(settings.TRANSACTION_INTERVAL)
            
        except Exception as e:
            logger.error(f"Error in transaction stream worker: {e}", exc_info=True)
            await asyncio.sleep(5)  # Wait before retry

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )