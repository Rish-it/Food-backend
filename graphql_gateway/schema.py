import strawberry
from typing import List, Optional
from uuid import UUID
import httpx
import asyncio
from strawberry.types import Info

# Import types from individual services
from user_service.gql.types import (
    Order as UserOrder, 
    Restaurant as UserRestaurant, 
    Rating,
    OrderInput, 
    RatingInput,
    PaginationInput as UserPagination
)
from restaurant_service.gql.types import (
    Restaurant as RestaurantType, 
    MenuItem, 
    Order as RestaurantOrder,
    RestaurantInput,
    MenuItemInput,
    OrderUpdateInput
)
from delivery_service.gql.types import (
    DeliveryAgent, 
    Order as DeliveryOrder,
    DeliveryAgentInput,
    LocationInput,
    AssignmentInput
)
@strawberry.type
class Query:
    @strawberry.field
    async def restaurants(self, info) -> List[UserRestaurant]:
        """Get all available restaurants from user service"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8001/graphql",
                json={
                    "query": """
                    query {
                        restaurants {
                            id
                            name
                            cuisineType
                            address
                            isOnline
                            operationHours
                            menuItems {
                                id
                                name
                                description
                                price
                                category
                                isAvailable
                                imageUrl
                            }
                        }
                    }
                    """
                }
            )
            data = response.json()
            return data.get("data", {}).get("restaurants", [])

    @strawberry.field
    async def restaurant(self, restaurant_id: UUID) -> Optional[UserRestaurant]:
        """Get restaurant with menu from user service"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8001/graphql",
                json={
                    "query": """
                    query GetRestaurant($restaurantId: UUID!) {
                        restaurant(restaurantId: $restaurantId) {
                            id
                            name
                            cuisineType
                            address
                            isOnline
                            operationHours
                            menuItems {
                                id
                                name
                                description
                                price
                                category
                                isAvailable
                                imageUrl
                            }
                        }
                    }
                    """,
                    "variables": {"restaurantId": str(restaurant_id)}
                }
            )
            data = response.json()
            return data.get("data", {}).get("restaurant")

    @strawberry.field
    async def user_orders(self, user_id: UUID) -> List[UserOrder]:
        """Get user orders from user service"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8001/graphql",
                json={
                    "query": """
                    query GetUserOrders($userId: UUID!) {
                        userOrders(userId: $userId) {
                            items {
                                id
                                userId
                                restaurantId
                                deliveryAgentId
                                status
                                totalAmount
                                deliveryAddress
                                specialInstructions
                                placedAt
                                acceptedAt
                                deliveredAt
                                orderItems {
                                    id
                                    menuItemId
                                    quantity
                                    unitPrice
                                    totalPrice
                                }
                            }
                        }
                    }
                    """,
                    "variables": {"userId": str(user_id)}
                }
            )
            data = response.json()
            return data.get("data", {}).get("userOrders", {}).get("items", [])

    @strawberry.field
    async def restaurant_orders(self, restaurant_id: UUID) -> List[RestaurantOrder]:
        """Get restaurant orders from restaurant service"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8002/graphql",
                json={
                    "query": """
                    query GetRestaurantOrders($restaurantId: UUID!) {
                        restaurantOrders(restaurantId: $restaurantId) {
                            items {
                                id
                                userId
                                restaurantId
                                deliveryAgentId
                                status
                                totalAmount
                                deliveryAddress
                                specialInstructions
                                placedAt
                                acceptedAt
                                deliveredAt
                                estimatedPrepTime
                            }
                        }
                    }
                    """,
                    "variables": {"restaurantId": str(restaurant_id)}
                }
            )
            data = response.json()
            return data.get("data", {}).get("restaurantOrders", {}).get("items", [])

    @strawberry.field
    async def delivery_agents(self, available_only: bool = False) -> List[DeliveryAgent]:
        """Get delivery agents from delivery service"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8003/graphql",
                json={
                    "query": """
                    query GetDeliveryAgents($availableOnly: Boolean!) {
                        deliveryAgents(availableOnly: $availableOnly) {
                            items {
                                id
                                name
                                email
                                phone
                                vehicleType
                                isAvailable
                                currentLocation {
                                    latitude
                                    longitude
                                    address
                                }
                                deliveriesCompleted
                                averageRating
                                createdAt
                            }
                        }
                    }
                    """,
                    "variables": {"availableOnly": available_only}
                }
            )
            data = response.json()
            return data.get("data", {}).get("deliveryAgents", {}).get("items", [])
@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_order(
        self, 
        user_id: UUID, 
        order_input: OrderInput
    ) -> UserOrder:
        """Create order through user service"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8001/graphql",
                json={
                    "query": """
                    mutation CreateOrder($userId: UUID!, $orderInput: OrderInput!) {
                        createOrder(userId: $userId, orderInput: $orderInput) {
                            id
                            userId
                            restaurantId
                            deliveryAgentId
                            status
                            totalAmount
                            deliveryAddress
                            specialInstructions
                            placedAt
                            acceptedAt
                            deliveredAt
                            orderItems {
                                id
                                menuItemId
                                quantity
                                unitPrice
                                totalPrice
                            }
                        }
                    }
                    """,
                    "variables": {
                        "userId": str(user_id),
                        "orderInput": {
                            "restaurantId": str(order_input.restaurant_id),
                            "deliveryAddress": order_input.delivery_address,
                            "items": [
                                {
                                    "menuItemId": str(item.menu_item_id),
                                    "quantity": item.quantity
                                }
                                for item in order_input.items
                            ],
                            "specialInstructions": order_input.special_instructions
                        }
                    }
                }
            )
            data = response.json()
            return data.get("data", {}).get("createOrder")

    @strawberry.mutation
    async def accept_order(
        self, 
        order_id: UUID, 
        restaurant_id: UUID,
        estimated_prep_time: Optional[int] = None
    ) -> Optional[RestaurantOrder]:
        """Accept order through restaurant service"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8002/graphql",
                json={
                    "query": """
                    mutation AcceptOrder($orderId: UUID!, $restaurantId: UUID!, $estimatedPrepTime: Int) {
                        acceptOrder(orderId: $orderId, restaurantId: $restaurantId, estimatedPrepTime: $estimatedPrepTime) {
                            id
                            status
                            estimatedPrepTime
                        }
                    }
                    """,
                    "variables": {
                        "orderId": str(order_id),
                        "restaurantId": str(restaurant_id),
                        "estimatedPrepTime": estimated_prep_time
                    }
                }
            )
            data = response.json()
            return data.get("data", {}).get("acceptOrder")

    @strawberry.mutation
    async def assign_order_to_agent(
        self, 
        assignment_input: AssignmentInput
    ) -> bool:
        """Assign order to delivery agent through delivery service"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8003/graphql",
                json={
                    "query": """
                    mutation AssignOrder($assignmentInput: AssignmentInput!) {
                        assignOrder(assignmentInput: $assignmentInput)
                    }
                    """,
                    "variables": {
                        "assignmentInput": {
                            "orderId": str(assignment_input.order_id),
                            "deliveryAgentId": str(assignment_input.delivery_agent_id),
                            "restaurantId": str(assignment_input.restaurant_id)
                        }
                    }
                }
            )
            data = response.json()
            return data.get("data", {}).get("assignOrder", False)

    @strawberry.mutation
    async def mark_order_delivered(
        self, 
        order_id: UUID, 
        agent_id: UUID
    ) -> Optional[DeliveryOrder]:
        """Mark order as delivered through delivery service"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8003/graphql",
                json={
                    "query": """
                    mutation MarkOrderDelivered($orderId: UUID!, $agentId: UUID!) {
                        markOrderDelivered(orderId: $orderId, agentId: $agentId) {
                            id
                            status
                            deliveredAt
                        }
                    }
                    """,
                    "variables": {
                        "orderId": str(order_id),
                        "agentId": str(agent_id)
                    }
                }
            )
            data = response.json()
            return data.get("data", {}).get("markOrderDelivered")
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        strawberry.extensions.QueryDepthLimiter(max_depth=15),
        strawberry.extensions.ValidationCache(maxsize=100),
    ]
) 