import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import {
  getConversations,
  getConversationMessages,
  sendMessage,
  markMessagesRead,
  getOrCreateOrderConversation,
} from '../../services/api';
import { Conversation, Message } from '../../types';
import {
  MessageSquare,
  Send,
  CheckCheck,
  Check,
  Clock,
  Sprout,
  Building2,
  Package,
  AlertCircle,
  Search,
  ArrowLeft,
  Lock,
} from 'lucide-react';

export const MessagesPage: React.FC = () => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const [searchParams, setSearchParams] = useSearchParams();

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConvId, setSelectedConvId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [inputText, setInputText] = useState('');
  const [sending, setSending] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const pollTimerRef = useRef<any>(null);

  const selectedConv = conversations.find((c) => c.id === selectedConvId) || null;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Load conversation list
  const loadConversations = useCallback(async (selectFirstIfNone = false) => {
    try {
      const res = await getConversations();
      const list: Conversation[] = res.data;
      setConversations(list);

      // Handle query param routing (?conversationId=... or ?orderId=...)
      const queryConvId = searchParams.get('conversationId');
      const queryOrderId = searchParams.get('orderId');

      if (queryOrderId) {
        // Resolve or create conversation for this order
        try {
          const orderConvRes = await getOrCreateOrderConversation(Number(queryOrderId));
          const newConv: Conversation = orderConvRes.data;
          setSelectedConvId(newConv.id);
          // Update URL to conversationId
          setSearchParams({ conversationId: String(newConv.id) });
          return;
        } catch (e) {
          console.error('Failed to resolve conversation for order', e);
        }
      }

      if (queryConvId) {
        setSelectedConvId(Number(queryConvId));
      } else if (selectFirstIfNone && list.length > 0 && !selectedConvId) {
        setSelectedConvId(list[0].id);
        setSearchParams({ conversationId: String(list[0].id) });
      }
    } catch (err: any) {
      console.error('Failed to load conversations', err);
      setErrorMsg('Failed to load conversations. Please try again.');
    } finally {
      setLoadingList(false);
    }
  }, [searchParams, setSearchParams, selectedConvId]);

  // Load messages for selected conversation
  const loadMessages = useCallback(async (convId: number, isSilent = false) => {
    if (!convId) return;
    if (!isSilent) setLoadingMessages(true);
    try {
      const res = await getConversationMessages(convId);
      setMessages(res.data);
      if (!isSilent) {
        setTimeout(scrollToBottom, 100);
      }
      // Mark as read
      await markMessagesRead(convId);
      // Update local unread counter on that conversation
      setConversations((prev) =>
        prev.map((c) => (c.id === convId ? { ...c, unread_count: 0 } : c))
      );
    } catch (err: any) {
      console.error('Failed to load messages', err);
    } finally {
      if (!isSilent) setLoadingMessages(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    loadConversations(true);
  }, []);

  // Whenever selected conversation changes
  useEffect(() => {
    if (selectedConvId) {
      loadMessages(selectedConvId);
      setErrorMsg(null);
    } else {
      setMessages([]);
    }
  }, [selectedConvId, loadMessages]);

  // 6-second polling when tab is active
  useEffect(() => {
    if (!selectedConvId) return;

    const tick = () => {
      if (document.hidden) return; // Pause polling if tab is backgrounded
      loadMessages(selectedConvId, true);
    };

    pollTimerRef.current = setInterval(tick, 6000);

    return () => {
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    };
  }, [selectedConvId, loadMessages]);

  const handleSelectConversation = (conv: Conversation) => {
    setSelectedConvId(conv.id);
    setSearchParams({ conversationId: String(conv.id) });
  };

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputText.trim() || !selectedConvId || sending) return;

    const trimmed = inputText.trim();
    setSending(true);
    setErrorMsg(null);

    try {
      const res = await sendMessage(selectedConvId, { content: trimmed });
      setMessages((prev) => [...prev, res.data]);
      setInputText('');
      setTimeout(scrollToBottom, 50);

      // Update snippet in list
      setConversations((prev) =>
        prev.map((c) =>
          c.id === selectedConvId
            ? { ...c, last_message: trimmed, last_message_at: new Date().toISOString() }
            : c
        )
      );
    } catch (err: any) {
      const detail = err.response?.data?.detail || 'Failed to send message';
      setErrorMsg(detail);
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Helper to determine the other participant
  const getOtherParty = (conv: Conversation) => {
    if (user?.id === conv.buyer.id) {
      return {
        name: conv.farmer.full_name,
        role: 'FARMER',
        sub: conv.farmer.business_or_farm_name || conv.farmer.district || 'Grower',
      };
    }
    return {
      name: conv.buyer.full_name,
      role: 'BUYER',
      sub: conv.buyer.business_or_farm_name || conv.buyer.district || 'Commercial Buyer',
    };
  };

  const formatTime = (isoString?: string) => {
    if (!isoString) return '';
    const d = new Date(isoString);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatDate = (isoString?: string) => {
    if (!isoString) return '';
    const d = new Date(isoString);
    return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
  };

  const filteredConversations = conversations.filter((c) => {
    const other = getOtherParty(c);
    const term = searchTerm.toLowerCase();
    return (
      other.name.toLowerCase().includes(term) ||
      c.order_summary.commodity_name.toLowerCase().includes(term) ||
      `#${c.order_id}`.includes(term)
    );
  });

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-slate-100 flex flex-col">
      {/* Top Banner */}
      <div className="bg-white border-b border-slate-200 px-4 sm:px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-900 flex items-center space-x-2">
              <MessageSquare className="w-5 h-5 text-emerald-600" />
              <span>{(t as any).messages?.title || 'Direct Messages'}</span>
            </h1>
            <p className="text-xs text-slate-500">
              {(t as any).messages?.subtitle || 'Private, authenticated communications with verified trading partners'}
            </p>
          </div>
          <div className="text-xs bg-emerald-50 text-emerald-700 px-3 py-1.5 rounded-full font-medium border border-emerald-200 hidden sm:flex items-center space-x-1">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Transaction-Linked & End-to-End Authenticated</span>
          </div>
        </div>
      </div>

      {/* Main Container */}
      <div className="max-w-7xl mx-auto w-full flex-1 p-2 sm:p-6 flex flex-col">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 flex-1 flex flex-col md:flex-row overflow-hidden min-h-[600px]">
          
          {/* Left Pane: Conversation List */}
          <div
            className={`w-full md:w-80 lg:w-96 border-r border-slate-200 flex flex-col bg-slate-50/50 ${
              selectedConvId ? 'hidden md:flex' : 'flex'
            }`}
          >
            {/* Search Bar */}
            <div className="p-3 border-b border-slate-200 bg-white">
              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="text"
                  placeholder="Search partner or commodity..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-emerald-500"
                />
              </div>
            </div>

            {/* Conversation List Content */}
            <div className="flex-1 overflow-y-auto divide-y divide-slate-100">
              {loadingList ? (
                <div className="p-8 text-center text-xs text-slate-400">Loading conversations...</div>
              ) : filteredConversations.length === 0 ? (
                <div className="p-8 text-center text-slate-500 space-y-2">
                  <MessageSquare className="w-8 h-8 text-slate-300 mx-auto" />
                  <p className="text-xs font-semibold">{(t as any).messages?.noConversations || 'No active conversations yet'}</p>
                  <p className="text-[11px] text-slate-400">
                    {(t as any).messages?.noConversationsDesc ||
                      'Conversations are established when an offer is accepted into a confirmed order.'}
                  </p>
                </div>
              ) : (
                filteredConversations.map((conv) => {
                  const other = getOtherParty(conv);
                  const isSelected = conv.id === selectedConvId;
                  return (
                    <button
                      key={conv.id}
                      onClick={() => handleSelectConversation(conv)}
                      className={`w-full text-left p-3.5 transition-colors flex items-start space-x-3 ${
                        isSelected
                          ? 'bg-emerald-50/70 border-l-4 border-emerald-600'
                          : 'hover:bg-slate-100/60'
                      }`}
                    >
                      {/* Avatar Icon */}
                      <div
                        className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 text-white ${
                          other.role === 'FARMER' ? 'bg-emerald-600' : 'bg-blue-600'
                        }`}
                      >
                        {other.role === 'FARMER' ? (
                          <Sprout className="w-5 h-5" />
                        ) : (
                          <Building2 className="w-5 h-5" />
                        )}
                      </div>

                      {/* Conversation Details */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-0.5">
                          <h4 className="text-xs font-semibold text-slate-900 truncate">{other.name}</h4>
                          <span className="text-[10px] text-slate-400 flex-shrink-0">
                            {formatDate(conv.last_message_at || conv.updated_at)}
                          </span>
                        </div>

                        {/* Order & Commodity Tag */}
                        <div className="flex items-center space-x-1.5 mb-1">
                          <span className="text-[10px] bg-slate-200/80 text-slate-700 px-1.5 py-0.2 rounded font-medium">
                            #{conv.order_id} {conv.order_summary.commodity_name}
                          </span>
                          {conv.is_messaging_closed && (
                            <span className="text-[10px] text-amber-600 flex items-center space-x-0.5">
                              <Lock className="w-2.5 h-2.5" />
                              <span>Closed</span>
                            </span>
                          )}
                        </div>

                        {/* Last message snippet & unread pill */}
                        <div className="flex items-center justify-between">
                          <p className="text-[11px] text-slate-500 truncate max-w-[190px]">
                            {conv.last_message || 'Order confirmed. Tap to coordinate delivery.'}
                          </p>
                          {conv.unread_count > 0 && (
                            <span className="bg-emerald-600 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full flex-shrink-0">
                              {conv.unread_count}
                            </span>
                          )}
                        </div>
                      </div>
                    </button>
                  );
                })
              )}
            </div>
          </div>

          {/* Right Pane: Active Chat Thread */}
          <div
            className={`flex-1 flex flex-col bg-slate-50/30 ${
              !selectedConvId ? 'hidden md:flex' : 'flex'
            }`}
          >
            {selectedConv ? (
              <>
                {/* Active Chat Header */}
                <div className="p-3.5 bg-white border-b border-slate-200 flex items-center justify-between shadow-xs">
                  <div className="flex items-center space-x-3 min-w-0">
                    {/* Mobile Back Button */}
                    <button
                      onClick={() => setSelectedConvId(null)}
                      className="md:hidden text-slate-500 hover:text-slate-800 p-1"
                    >
                      <ArrowLeft className="w-5 h-5" />
                    </button>

                    <div>
                      <div className="flex items-center space-x-2">
                        <h3 className="text-sm font-bold text-slate-900 truncate">
                          {getOtherParty(selectedConv).name}
                        </h3>
                        <span
                          className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${
                            getOtherParty(selectedConv).role === 'FARMER'
                              ? 'bg-emerald-100 text-emerald-800'
                              : 'bg-blue-100 text-blue-800'
                          }`}
                        >
                          {getOtherParty(selectedConv).role}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-500">
                        {getOtherParty(selectedConv).sub}
                      </p>
                    </div>
                  </div>

                  {/* Order Pill Link */}
                  <div className="text-right flex items-center space-x-3">
                    <div className="hidden sm:block text-right">
                      <div className="text-xs font-semibold text-slate-800">
                        Order #{selectedConv.order_id} ({selectedConv.order_summary.status})
                      </div>
                      <div className="text-[11px] text-slate-500">
                        {selectedConv.order_summary.quantity} {selectedConv.order_summary.unit} @ ₹{selectedConv.order_summary.price_per_unit}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Status Notice Banner (Closed / Disputed) */}
                {selectedConv.is_messaging_closed ? (
                  <div className="bg-amber-50 border-b border-amber-200 px-4 py-2 text-xs text-amber-800 flex items-center space-x-2">
                    <Lock className="w-4 h-4 text-amber-600 flex-shrink-0" />
                    <span>
                      {(t as any).messages?.closedNotice ||
                        'Messaging is closed for this order because it has completed or cancelled. Conversation history is preserved.'}
                    </span>
                  </div>
                ) : (
                  <div className="bg-emerald-50/60 border-b border-emerald-100 px-4 py-1.5 text-[11px] text-emerald-800 flex items-center justify-between">
                    <span>
                      Coordinate dispatch, farm pickup timing, and vehicle details directly with your partner.
                    </span>
                    <span className="text-slate-400 text-[10px] hidden sm:inline">
                      Commercial terms locked in Order #{selectedConv.order_id}
                    </span>
                  </div>
                )}

                {/* Error Banner */}
                {errorMsg && (
                  <div className="bg-red-50 border-b border-red-200 px-4 py-2 text-xs text-red-700 flex items-center justify-between">
                    <span>{errorMsg}</span>
                    <button onClick={() => setErrorMsg(null)} className="text-red-900 font-bold ml-2">
                      ✕
                    </button>
                  </div>
                )}

                {/* Message Bubbles Container */}
                <div className="flex-1 p-4 overflow-y-auto space-y-3">
                  {loadingMessages ? (
                    <div className="h-full flex items-center justify-center text-xs text-slate-400">
                      Loading message history...
                    </div>
                  ) : messages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-slate-400 space-y-2 p-6 text-center">
                      <MessageSquare className="w-10 h-10 text-slate-300" />
                      <p className="text-xs font-medium text-slate-600">Start the conversation</p>
                      <p className="text-[11px] text-slate-400 max-w-sm">
                        Introduce yourself and confirm logistics for Order #{selectedConv.order_id} (
                        {selectedConv.order_summary.commodity_name}).
                      </p>
                    </div>
                  ) : (
                    messages.map((m) => {
                      const isMine = m.is_mine || m.sender_id === user?.id;
                      return (
                        <div
                          key={m.id}
                          className={`flex flex-col ${isMine ? 'items-end' : 'items-start'}`}
                        >
                          <div
                            className={`max-w-[85%] sm:max-w-[70%] rounded-2xl px-4 py-2.5 shadow-xs ${
                              isMine
                                ? 'bg-emerald-600 text-white rounded-tr-none'
                                : 'bg-white border border-slate-200 text-slate-900 rounded-tl-none'
                            }`}
                          >
                            <p className="text-xs leading-relaxed whitespace-pre-wrap break-words">
                              {m.content}
                            </p>
                            <div
                              className={`flex items-center justify-end space-x-1 mt-1 text-[10px] ${
                                isMine ? 'text-emerald-100' : 'text-slate-400'
                              }`}
                            >
                              <span>{formatTime(m.created_at)}</span>
                              {isMine && (
                                <span title={m.is_read ? 'Read' : 'Delivered'}>
                                  {m.is_read ? (
                                    <CheckCheck className="w-3.5 h-3.5 text-emerald-200" />
                                  ) : (
                                    <Check className="w-3.5 h-3.5 text-emerald-200/70" />
                                  )}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })
                  )}
                  <div ref={messagesEndRef} />
                </div>

                {/* Message Input Form */}
                <div className="p-3 bg-white border-t border-slate-200">
                  <form onSubmit={handleSend} className="flex items-end space-x-2">
                    <textarea
                      value={inputText}
                      onChange={(e) => setInputText(e.target.value)}
                      onKeyDown={handleKeyDown}
                      disabled={selectedConv.is_messaging_closed || sending}
                      placeholder={
                        selectedConv.is_messaging_closed
                          ? 'Messaging is closed for this order.'
                          : (t as any).messages?.typePlaceholder ||
                            'Type your message here (e.g. logistics, pickup timing)...'
                      }
                      rows={2}
                      maxLength={2000}
                      className="flex-1 resize-none bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-emerald-500 disabled:bg-slate-100 disabled:text-slate-400"
                    />
                    <button
                      type="submit"
                      disabled={!inputText.trim() || selectedConv.is_messaging_closed || sending}
                      className="bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-200 text-white p-3 rounded-xl transition flex items-center justify-center flex-shrink-0 shadow-xs"
                      title={(t as any).messages?.send || 'Send'}
                    >
                      <Send className="w-4 h-4" />
                    </button>
                  </form>
                  <div className="flex justify-between items-center text-[10px] text-slate-400 px-1 mt-1">
                    <span>Press Enter to send, Shift+Enter for new line</span>
                    <span>{inputText.length} / 2000</span>
                  </div>
                </div>
              </>
            ) : (
              /* Empty State when no conversation selected */
              <div className="h-full flex flex-col items-center justify-center text-center p-8 text-slate-400 space-y-3">
                <div className="w-16 h-16 rounded-full bg-emerald-50 flex items-center justify-center text-emerald-600">
                  <MessageSquare className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-800">
                    {(t as any).messages?.selectConversation || 'Select a conversation'}
                  </h3>
                  <p className="text-xs text-slate-500 max-w-sm mt-1">
                    Choose a conversation from the left to coordinate delivery, pickup, and specifications with your trading partner.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
