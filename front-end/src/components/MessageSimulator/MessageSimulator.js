import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import LLMCallWindow from './components/LLMCallWindow/LLMCallWindow';
import './MessageSimulator.css';

const DEFAULT_API_KEY = 'cd0fd3314e8f1fe7cef737db4ac21778ccc7d5a97bbb33d9af17612e337231d6';

// Create axios instance with base URL
const api = axios.create({
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
    headers: {
        'content-type': 'application/json',
        'authorization': `Bearer ${DEFAULT_API_KEY}`
    },
    withCredentials: true  // Enable sending cookies
});

const MessageSimulator = () => {
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [userId, setUserId] = useState('72818df0-f5fd-4727-97bd-4e21f8430a9e'); // Default user ID
    const [businessId, setBusinessId] = useState('32a6f42a-b6cf-41e3-a970-bdb051784eff'); // Default business ID
    const [conversationId, setConversationId] = useState(null);
    const [internalApiKey, setInternalApiKey] = useState(DEFAULT_API_KEY);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Load all conversations when component mounts
    useEffect(() => {
        loadAllConversations();
    }, []);

    const loadAllConversations = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await api.get(`/api/simulate/user/${userId}/conversations`);
            
            if (response.data.success) {
                // Handle empty conversations array
                if (!response.data.conversations || response.data.conversations.length === 0) {
                    setMessages([]);
                    return;
                }

                // Flatten all messages from all conversations
                const allMessages = response.data.conversations.flatMap(conv => 
                    (conv.messages || []).map(msg => ({
                        ...msg,
                        conversation_id: conv.conversation_id
                    }))
                );
                
                // Sort messages by timestamp
                allMessages.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
                setMessages(allMessages);
            } else {
                setError('Failed to load conversations: ' + (response.data.error || 'Unknown error'));
            }
        } catch (err) {
            const errorMessage = err.response?.data?.error || err.message;
            if (errorMessage.includes('get_connection')) {
                setError('Database connection error. Please try again later.');
            } else {
                setError('Failed to load conversations: ' + errorMessage);
            }
            console.error('Error loading conversations:', err);
        } finally {
            setLoading(false);
        }
    };

    // Load conversation history when conversationId changes
    useEffect(() => {
        if (conversationId) {
            loadConversationHistory();
        }
    }, [conversationId]);

    const loadConversationHistory = async () => {
        try {
            const response = await api.get(`/api/simulate/conversation/${conversationId}`);
            if (response.data.success) {
                setMessages(response.data.messages);
            }
        } catch (err) {
            setError('Failed to load conversation history: ' + (err.response?.data?.error || err.message));
            console.error('Error loading conversation history:', err);
        }
    };

    const sendMessage = async (e) => {
        e.preventDefault();
        if (!newMessage.trim()) return;

        setLoading(true);
        setError(null);

        try {
            const response = await api.post('/api/simulate/message', {
                user_id: userId,
                business_id: businessId,
                message_content: newMessage,
                conversation_id: conversationId
            });

            if (response.data.success) {
                // Update conversation ID if this is a new conversation
                if (!conversationId && response.data.conversation_id) {
                    setConversationId(response.data.conversation_id);
                }
                
                // Add the new message to the list
                setMessages(prev => [...prev, {
                    content: newMessage,
                    sender: 'user',
                    timestamp: new Date().toISOString()
                }, {
                    content: response.data.content || response.data.message || response.data.response,
                    sender: 'assistant',
                    timestamp: new Date().toISOString()
                }]);

                setNewMessage('');
            } else {
                setError('Failed to process message: ' + (response.data.error || 'Unknown error'));
            }
        } catch (err) {
            setError('Failed to send message: ' + (err.response?.data?.error || err.message));
            console.error('Error sending message:', err);
        } finally {
            setLoading(false);
        }
    };

    // Memoize the message rendering to improve performance
    const renderMessages = useCallback(() => {
        return messages.map((message, index) => (
            <div 
                key={`${message.timestamp}-${index}`}
                className={`message ${message.sender === 'user' ? 'user-message' : 'assistant-message'}`}
            >
                <div className="message-content">{message.content}</div>
                <div className="message-timestamp">
                    {new Date(message.timestamp).toLocaleTimeString()}
                </div>
            </div>
        ));
    }, [messages]);

    return (
        <div className="message-simulator-container">
            <div className="message-simulator">
                <div className="simulator-header">
                    <h2>Message Simulator</h2>
                    <div className="user-info">
                        <input
                            type="text"
                            placeholder="User ID"
                            value={userId}
                            onChange={(e) => setUserId(e.target.value)}
                        />
                        <input
                            type="text"
                            placeholder="Business ID"
                            value={businessId}
                            onChange={(e) => setBusinessId(e.target.value)}
                        />
                        <input
                            type="text"
                            placeholder="Internal API Key"
                            value={internalApiKey}
                            onChange={(e) => setInternalApiKey(e.target.value)}
                        />
                        <button 
                            onClick={loadAllConversations}
                            className="refresh-button"
                            title="Refresh all conversations"
                            disabled={loading}
                        >
                            <i className="fas fa-sync-alt"></i> Refresh
                        </button>
                    </div>
                </div>

                <div className="messages-container">
                    {renderMessages()}
                    {loading && <div className="loading">Loading messages...</div>}
                    {error && <div className="error">{error}</div>}
                </div>

                <form onSubmit={sendMessage} className="message-input">
                    <input
                        type="text"
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        placeholder="Type your message..."
                        disabled={loading}
                    />
                    <button 
                        type="submit" 
                        disabled={loading || !newMessage.trim()}
                    >
                        Send
                    </button>
                </form>
            </div>

            <div className="llm-call-window-container">
                <LLMCallWindow internalApiKey={internalApiKey} />
            </div>
        </div>
    );
};

export default MessageSimulator; 