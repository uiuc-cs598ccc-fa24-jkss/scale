from server.apis.health_api_base import BaseHealthApi

class HealthService(BaseHealthApi):

    async def get_api_health(
        self,
    ) -> dict:
        """Health check endpoint.  Returns: - The health check response."""
        return {"status": "UP"}