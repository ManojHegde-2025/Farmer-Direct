export type UserRole = 'FARMER' | 'BUYER' | 'ADMIN';
export type District = 'UDUPI' | 'DAKSHINA_KANNADA';
export type VerificationStatus = 'PENDING' | 'SUBMITTED' | 'APPROVED' | 'REJECTED';
export type CommodityUnit = 'KG' | 'QUINTAL' | 'TONNE' | 'COUNT' | 'BUNCH' | 'DOZEN';
export type QualityGrade = 'A' | 'B' | 'C' | 'UNGRADED';
export type ListingStatus = 'DRAFT' | 'PENDING_REVIEW' | 'ACTIVE' | 'PARTIALLY_RESERVED' | 'SOLD_OUT' | 'EXPIRED' | 'SUSPENDED' | 'CANCELLED';
export type OfferStatus = 'PENDING' | 'COUNTERED' | 'ACCEPTED' | 'REJECTED' | 'WITHDRAWN' | 'EXPIRED';
export type OrderStatus = 'CREATED' | 'AWAITING_CONFIRMATION' | 'CONFIRMED' | 'PAYMENT_PENDING' | 'PAYMENT_CONFIRMED' | 'READY_FOR_PICKUP' | 'DISPATCHED' | 'DELIVERED' | 'COMPLETED' | 'CANCELLED' | 'DISPUTED';
export type FulfilmentMethod = 'BUYER_PICKUP' | 'SELLER_DELIVERY' | 'THIRD_PARTY';

export interface User {
  id: number;
  email: string;
  phone?: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  farmer_profile?: FarmerProfile;
  buyer_profile?: BuyerProfile;
}

export interface FarmerProfile {
  id: number;
  farm_name?: string;
  farm_location?: string;
  district?: District;
  taluk?: string;
  village?: string;
  farm_size_acres?: number;
  primary_crops?: string;
  description?: string;
  verification_status: VerificationStatus;
  bank_account_verified: boolean;
}

export interface BuyerProfile {
  id: number;
  business_name?: string;
  business_type?: string;
  district?: string;
  taluk?: string;
  description?: string;
  verification_status: VerificationStatus;
  gst_number?: string;
}

export interface Commodity {
  id: number;
  name: string;
  name_kn?: string;
  category?: string;
  unit: CommodityUnit;
  description?: string;
  icon?: string;
  is_active: boolean;
}

export interface Listing {
  id: number;
  title: string;
  description?: string;
  commodity_id: number;
  commodity_name?: string;
  commodity_name_kn?: string;
  commodity?: Commodity;
  variety?: string;
  quality_grade: QualityGrade;
  quantity: number;
  available_quantity: number;
  unit: CommodityUnit;
  price_per_unit: number;
  min_order_quantity?: number;
  images?: any;
  status: ListingStatus;
  harvest_date?: string;
  available_from?: string;
  available_until?: string;
  pickup_location?: string;
  delivery_available: boolean;
  delivery_radius_km?: number;
  farmer?: {
    id: number;
    full_name: string;
    district?: District;
    taluk?: string;
    village?: string;
    farm_name?: string;
    is_verified: boolean;
  };
  created_at: string;
  updated_at?: string;
}

export interface BuyerRequirement {
  id: number;
  buyer_id: number;
  commodity_id: number;
  commodity_name?: string;
  commodity_name_kn?: string;
  unit?: string;
  variety_preference?: string;
  quality_preference?: string;
  quantity_needed: number;
  max_price_per_unit?: number;
  delivery_location?: string;
  delivery_district?: string;
  needed_by?: string;
  is_active: boolean;
  created_at: string;
}

export interface ReferencePrice {
  id: number;
  commodity_id: number;
  commodity_name?: string;
  variety?: string;
  market?: string;
  locality?: string;
  price: number;
  unit: string;
  observation_date: string;
  source?: string;
  source_url?: string;
  classification: string;
  quality_grade?: string;
  is_demonstration: boolean;
}

export interface Offer {
  id: number;
  listing_id: number;
  listing_title?: string;
  commodity_name?: string;
  unit?: string;
  buyer_id: number;
  buyer_name?: string;
  seller_id: number;
  seller_name?: string;
  quantity: number;
  price_per_unit: number;
  total_price: number;
  delivery_method?: string;
  payment_terms?: string;
  message?: string;
  status: OfferStatus;
  parent_offer_id?: number;
  is_incoming?: boolean;
  created_at: string;
}

export interface Order {
  id: number;
  offer_id?: number;
  listing_id: number;
  listing_title?: string;
  commodity_id: number;
  commodity_name?: string;
  unit?: string;
  buyer_id: number;
  buyer_name?: string;
  seller_id: number;
  seller_name?: string;
  quantity: number;
  reserved_quantity: number;
  dispatched_quantity: number;
  delivered_quantity: number;
  price_per_unit: number;
  total_price: number;
  status: OrderStatus;
  fulfilment_method?: string;
  is_buyer?: boolean;
  is_seller?: boolean;
  payments?: any[];
  deliveries?: any[];
  disputes?: any[];
  reviews?: any[];
  created_at: string;
  updated_at?: string;
}

export interface MatchResult {
  listing_id: number;
  listing: Listing;
  match_score: number;
  score_breakdown: Record<string, number>;
  match_reasons: string[];
  explanation: string;
  fulfillable_quantity: number;
}

export interface ConversationParticipant {
  id: number;
  full_name: string;
  role: string;
  district?: string;
  business_or_farm_name?: string;
}

export interface ConversationOrderSummary {
  id: number;
  status: OrderStatus;
  commodity_name: string;
  quantity: number;
  unit: string;
  price_per_unit: number;
  total_price: number;
}

export interface Message {
  id: number;
  conversation_id: number;
  sender_id: number;
  sender_name: string;
  sender_role: string;
  content: string;
  is_read: boolean;
  read_at?: string;
  created_at: string;
  is_mine: boolean;
}

export interface Conversation {
  id: number;
  order_id: number;
  buyer: ConversationParticipant;
  farmer: ConversationParticipant;
  order_summary: ConversationOrderSummary;
  last_message?: string;
  last_message_at?: string;
  unread_count: number;
  is_messaging_closed: boolean;
  created_at: string;
  updated_at: string;
}

export interface SendMessagePayload {
  content: string;
}
