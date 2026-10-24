import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auto-attach JWT Bearer token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('farmerdirect_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for token expiry handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('farmerdirect_token');
      localStorage.removeItem('farmerdirect_user');
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register' && window.location.pathname !== '/') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Commodity API
export const getCommodities = () => api.get('/commodities/');

// Listings API
export const getListings = (params?: any) => api.get('/listings/', { params });
export const getListingById = (id: number) => api.get(`/listings/${id}`);
export const createListing = (data: any) => api.post('/listings/', data);
export const updateListing = (id: number, data: any) => api.put(`/listings/${id}`, data);
export const updateListingStatus = (id: number, status: string) => api.patch(`/listings/${id}/status`, { status });

// Requirements API
export const getRequirements = (params?: any) => api.get('/requirements/', { params });
export const getRequirementById = (id: number) => api.get(`/requirements/${id}`);
export const createRequirement = (data: any) => api.post('/requirements/', data);
export const deleteRequirement = (id: number) => api.delete(`/requirements/${id}`);

// Matching API
export const getMatchesForRequirement = (reqId: number, params?: any) => api.get(`/matching/requirement/${reqId}`, { params });
export const getBuyersForListing = (listingId: number) => api.get(`/matching/listing/${listingId}/buyers`);

// Offers API
export const createOffer = (data: any) => api.post('/offers/', data);
export const counterOffer = (id: number, data: any) => api.post(`/offers/${id}/counter`, data);
export const acceptOffer = (id: number) => api.post(`/offers/${id}/accept`);
export const rejectOffer = (id: number) => api.post(`/offers/${id}/reject`);
export const getOffers = (params?: any) => api.get('/offers/', { params });
export const getNegotiationHistory = (id: number) => api.get(`/offers/${id}/history`);

// Orders API
export const getOrders = (params?: any) => api.get('/orders/', { params });
export const getOrderById = (id: number) => api.get(`/orders/${id}`);
export const updateOrderStatus = (id: number, status: string) => api.patch(`/orders/${id}/status`, { status });
export const getOrderBreakdown = (id: number) => api.get(`/orders/${id}/breakdown`);

// Payments API
export const recordPayment = (data: any) => api.post('/payments/', data);

// Deliveries API
export const createDelivery = (data: any) => api.post('/deliveries/', data);
export const updateDelivery = (id: number, data: any) => api.patch(`/deliveries/${id}`, data);

// Reference Prices API
export const getReferencePrices = (params?: any) => api.get('/reference-prices/', { params });
export const getCommodityReferencePrice = (commodityId: number) => api.get(`/reference-prices/commodity/${commodityId}`);

// Farmer API
export const getFarmerProfile = () => api.get('/farmers/profile');
export const updateFarmerProfile = (data: any) => api.put('/farmers/profile', data);
export const submitFarmerVerification = (data: any) => api.post('/farmers/verification', data);
export const getFarmerStats = () => api.get('/farmers/dashboard-stats');

// Buyer API
export const getBuyerProfile = () => api.get('/buyers/profile');
export const updateBuyerProfile = (data: any) => api.put('/buyers/profile', data);
export const getBuyerStats = () => api.get('/buyers/dashboard-stats');

// Admin API
export const getAdminStats = () => api.get('/admin/stats');
export const getPendingVerifications = () => api.get('/admin/verifications');
export const verifyFarmer = (id: number, decision: any) => api.patch(`/admin/verify/farmer/${id}`, decision);
export const verifyBuyer = (id: number, decision: any) => api.patch(`/admin/verify/buyer/${id}`, decision);
export const getAdminUsers = (params?: any) => api.get('/admin/users', { params });
export const updateUserStatus = (id: number, data: any) => api.patch(`/admin/users/${id}`, data);

// Reviews & Disputes
export const createReview = (data: any) => api.post('/reviews/', data);
export const getUserReviews = (userId: number) => api.get(`/reviews/user/${userId}`);
export const raiseDispute = (data: any) => api.post('/disputes/', data);
export const getDisputes = () => api.get('/disputes/');
export const resolveDispute = (id: number, data: any) => api.patch(`/disputes/${id}/resolve`, data);

// Conversations & Messaging API
export const getConversations = () => api.get('/conversations/');
export const getConversationById = (id: number) => api.get(`/conversations/${id}`);
export const getOrCreateOrderConversation = (orderId: number) => api.post(`/conversations/order/${orderId}`);
export const getConversationMessages = (id: number, params?: any) => api.get(`/conversations/${id}/messages`, { params });
export const sendMessage = (id: number, data: { content: string }) => api.post(`/conversations/${id}/messages`, data);
export const markMessagesRead = (id: number) => api.post(`/conversations/${id}/read`);
