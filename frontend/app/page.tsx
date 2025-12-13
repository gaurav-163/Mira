'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Send, 
  Sparkles, 
  Brain,
  Loader2,
  FileText,
  Trash2,
  BookOpen,
  ChevronDown,
  Menu,
  X,
  MessageSquare,
  Zap,
  Shield,
  Star,
  Copy,
  Check,
  ThumbsUp,
  ThumbsDown,
  RefreshCw,
  Settings,
  Plus,
  Search,
  Clock,
  TrendingUp
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import axios from 'axios'
import { useTypingEffect } from '@/src/hooks/useTypingEffect'

interface Message {
  role: 'user' | 'assistant'
  content: string
  source_type?: 'knowledge_base' | 'general_knowledge'
  timestamp?: Date
  sources?: Array<{
    content: string
    source?: string
    page?: number | string
    title?: string
    relevance?: number
    relevance_score?: string
    extraction_method?: string
  }>
}

interface ChatSession {
  id: string
  title: string
  timestamp: Date
  preview: string
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [initializing, setInitializing] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)
  const [hoveredMessage, setHoveredMessage] = useState<number | null>(null)
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string>('default')
  const [searchQuery, setSearchQuery] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  
  // Typing effect for "Mira"
  const { displayedText: typedTitle, isComplete: titleComplete } = useTypingEffect('Mira', 150, 500)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    const savedMessages = localStorage.getItem('chat_messages')
    if (savedMessages) {
      setMessages(JSON.parse(savedMessages))
    }
    
    const savedSessions = localStorage.getItem('chat_sessions')
    if (savedSessions) {
      setChatSessions(JSON.parse(savedSessions))
    }

    initializeBackend()
  }, [])

  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('chat_messages', JSON.stringify(messages))
      updateChatSession()
    }
  }, [messages])

  const initializeBackend = async () => {
    setInitializing(true)
    try {
      await axios.post('http://localhost:8000/api/initialize')
    } catch (error) {
      console.error('Failed to initialize:', error)
    } finally {
      setInitializing(false)
    }
  }

  const updateChatSession = () => {
    if (messages.length === 0) return
    
    const firstUserMessage = messages.find(m => m.role === 'user')
    const title = firstUserMessage?.content.substring(0, 50) || 'New Chat'
    const preview = messages[messages.length - 1]?.content.substring(0, 100) || ''
    
    const updatedSessions = chatSessions.filter(s => s.id !== currentSessionId)
    updatedSessions.unshift({
      id: currentSessionId,
      title,
      preview,
      timestamp: new Date()
    })
    
    setChatSessions(updatedSessions.slice(0, 20))
    localStorage.setItem('chat_sessions', JSON.stringify(updatedSessions.slice(0, 20)))
  }

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await axios.post('http://localhost:8000/api/chat', {
        message: input
      })

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.answer,
        source_type: response.data.source_type,
        sources: response.data.sources,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const clearChat = async () => {
    setMessages([])
    localStorage.removeItem('chat_messages')
    try {
      await axios.post('http://localhost:8000/api/clear')
    } catch (error) {
      console.error('Failed to clear:', error)
    }
  }

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text)
    setCopiedIndex(index)
    setTimeout(() => setCopiedIndex(null), 2000)
  }

  const createNewChat = () => {
    clearChat()
    setCurrentSessionId(`chat_${Date.now()}`)
  }

  const loadChatSession = (session: ChatSession) => {
    // In a real app, you'd load the actual messages
    setCurrentSessionId(session.id)
  }

  return (
    <div className="h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex overflow-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <motion.div 
          animate={{ 
            scale: [1, 1.2, 1],
            x: [0, 50, 0],
            y: [0, 30, 0]
          }}
          transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-gradient-to-br from-blue-500/20 via-cyan-500/20 to-purple-500/20 rounded-full blur-3xl"
        />
        <motion.div 
          animate={{ 
            scale: [1, 1.3, 1],
            x: [0, -50, 0],
            y: [0, -30, 0]
          }}
          transition={{ duration: 25, repeat: Infinity, ease: "easeInOut" }}
          className="absolute bottom-1/4 right-1/4 w-[600px] h-[600px] bg-gradient-to-br from-purple-500/20 via-pink-500/20 to-cyan-500/20 rounded-full blur-3xl"
        />
        <motion.div 
          animate={{ 
            scale: [1, 1.1, 1],
            rotate: [0, 180, 360]
          }}
          transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
          className="absolute top-1/2 left-1/2 w-[400px] h-[400px] bg-gradient-to-br from-blue-500/10 to-cyan-500/10 rounded-full blur-3xl"
        />
      </div>

      {/* Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ x: -320 }}
            animate={{ x: 0 }}
            exit={{ x: -320 }}
            transition={{ type: 'spring', damping: 20 }}
            className="w-80 backdrop-blur-2xl border-r border-slate-700/30 flex flex-col relative z-10"
            style={{
              background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.4) 0%, rgba(30, 41, 59, 0.3) 100%)'
            }}
          >
            {/* Sidebar Header */}
            <div className="p-4 border-b border-slate-700/50">
              <button
                onClick={createNewChat}
                className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-gradient-to-r from-blue-600 via-cyan-600 to-blue-600 hover:from-blue-500 hover:via-cyan-500 hover:to-blue-500 rounded-xl text-white font-medium transition-all duration-300 shadow-lg hover:shadow-blue-500/50 transform hover:scale-105"
              >
                <Plus className="w-5 h-5" />
                <span>New Chat</span>
              </button>
            </div>

            {/* Search */}
            <div className="p-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search conversations..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-slate-800/50 border border-slate-700/50 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent"
                />
              </div>
            </div>

            {/* Chat History */}
            <div className="flex-1 overflow-y-auto px-3 space-y-2">
              {chatSessions.map((session) => (
                <motion.button
                  key={session.id}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => loadChatSession(session)}
                  className="w-full text-left p-3 rounded-xl bg-slate-800/30 hover:bg-slate-800/50 border border-slate-700/30 hover:border-blue-500/30 transition-all duration-200"
                >
                  <div className="flex items-start space-x-3">
                    <MessageSquare className="w-4 h-4 text-blue-400 mt-1 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-200 truncate">{session.title}</p>
                      <p className="text-xs text-slate-500 truncate mt-1">{session.preview}</p>
                      <div className="flex items-center space-x-2 mt-2">
                        <Clock className="w-3 h-3 text-slate-600" />
                        <span className="text-xs text-slate-600">
                          {new Date(session.timestamp).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </motion.button>
              ))}
            </div>

            {/* Sidebar Footer */}
            <div className="p-4 border-t border-slate-700/50">
              <div className="flex items-center justify-between text-xs text-slate-500">
                <div className="flex items-center space-x-1">
                  <Shield className="w-3 h-3" />
                  <span>Secure & Private</span>
                </div>
                <button className="hover:text-blue-400 transition-colors">
                  <Settings className="w-4 h-4" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="flex-1 flex flex-col relative z-10">
        {/* Header */}
        <div className="bg-slate-900/20 backdrop-blur-2xl border-b border-slate-700/30 px-6 py-4" style={{
          background: 'linear-gradient(180deg, rgba(15, 23, 42, 0.3) 0%, rgba(30, 41, 59, 0.2) 100%)'
        }}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 hover:bg-slate-800/50 rounded-lg transition-colors"
              >
                {sidebarOpen ? <X className="w-5 h-5 text-slate-400" /> : <Menu className="w-5 h-5 text-slate-400" />}
              </button>
              <div className="flex items-center space-x-3">
                <div className="relative">
                  <motion.div 
                    animate={{ 
                      boxShadow: [
                        '0 0 20px rgba(59, 130, 246, 0.5)',
                        '0 0 40px rgba(6, 182, 212, 0.6)',
                        '0 0 20px rgba(59, 130, 246, 0.5)'
                      ]
                    }}
                    transition={{ duration: 3, repeat: Infinity }}
                    className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 via-cyan-500 to-purple-600 flex items-center justify-center"
                  >
                    <Brain className="w-6 h-6 text-white" />
                  </motion.div>
                  <motion.div 
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="absolute -bottom-1 -right-1 w-4 h-4 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full border-2 border-slate-900"
                  />
                </div>
                <div>
                  <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-400 bg-clip-text text-transparent">
                    {typedTitle}
                    {!titleComplete && (
                      <motion.span
                        animate={{ opacity: [1, 0] }}
                        transition={{ duration: 0.8, repeat: Infinity }}
                        className="inline-block w-0.5 h-5 bg-blue-400 ml-1"
                      />
                    )}
                  </h1>
                  <div className="flex items-center space-x-2 text-xs text-slate-500">
                    <div className="flex items-center space-x-1">
                      <Zap className="w-3 h-3 text-green-500" />
                      <span>Online</span>
                    </div>
                    <span>•</span>
                    <span>AI-Powered Knowledge Assistant</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {messages.length > 0 && (
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={clearChat}
                  className="px-3 py-1.5 bg-red-500/10 border border-red-500/30 hover:bg-red-500/20 rounded-lg flex items-center space-x-2 transition-all duration-200 group"
                >
                  <Trash2 className="w-4 h-4 text-red-400 group-hover:text-red-300" />
                  <span className="text-xs font-medium text-red-400 group-hover:text-red-300">Clear Chat</span>
                </motion.button>
              )}
              <div className="px-3 py-1.5 bg-blue-500/10 border border-blue-500/30 rounded-lg flex items-center space-x-2">
                <TrendingUp className="w-4 h-4 text-blue-400" />
                <span className="text-xs font-medium text-blue-400">{messages.length} messages</span>
              </div>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center p-8">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center"
              >
                <motion.h1 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3, type: "spring" }}
                  className="text-9xl font-bold"
                >
                  <motion.span 
                    animate={{
                      backgroundPosition: ['0% 50%', '100% 50%', '0% 50%']
                    }}
                    transition={{ duration: 5, repeat: Infinity, ease: "linear" }}
                    className="bg-gradient-to-r from-blue-400 via-cyan-400 via-purple-400 to-blue-400 bg-clip-text text-transparent"
                    style={{ backgroundSize: '200% auto' }}
                  >
                    {typedTitle}
                    {!titleComplete && (
                      <motion.span
                        animate={{ opacity: [1, 0] }}
                        transition={{ duration: 0.8, repeat: Infinity }}
                        className="inline-block w-1 h-20 bg-cyan-400 ml-2"
                      />
                    )}
                  </motion.span>
                </motion.h1>
              </motion.div>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto w-full px-6 py-8 space-y-6">
              <AnimatePresence>
                {messages.map((message, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    transition={{ duration: 0.3 }}
                    onMouseEnter={() => setHoveredMessage(index)}
                    onMouseLeave={() => setHoveredMessage(null)}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} group`}
                  >
                    <div className={`max-w-[80%] ${message.role === 'user' ? 'order-2' : 'order-1'}`}>
                      {message.role === 'assistant' && (
                        <div className="flex items-center space-x-3 mb-3">
                          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
                            <Sparkles className="w-4 h-4 text-white" />
                          </div>
                          <span className="text-sm font-medium text-slate-400">AI Assistant</span>
                          {message.source_type === 'knowledge_base' && (
                            <div className="flex items-center space-x-1 px-2 py-1 bg-blue-500/10 border border-blue-500/30 rounded-md">
                              <BookOpen className="w-3 h-3 text-blue-400" />
                              <span className="text-xs text-blue-400">Knowledge Base</span>
                            </div>
                          )}
                        </div>
                      )}
                      
                      <div className={`relative rounded-2xl px-6 py-4 ${
                        message.role === 'user'
                          ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30'
                          : 'bg-slate-800/50 backdrop-blur-xl border border-slate-700/50 text-slate-100'
                      }`}>
                        <ReactMarkdown className="prose prose-invert max-w-none prose-p:leading-relaxed prose-pre:bg-slate-900/50 prose-pre:border prose-pre:border-slate-700/50">
                          {message.content}
                        </ReactMarkdown>
                        
                        {/* Action Buttons */}
                        {message.role === 'assistant' && hoveredMessage === index && (
                          <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="flex items-center space-x-2 mt-4 pt-4 border-t border-slate-700/50"
                          >
                            <button
                              onClick={() => copyToClipboard(message.content, index)}
                              className="p-2 hover:bg-slate-700/50 rounded-lg transition-colors"
                              title="Copy"
                            >
                              {copiedIndex === index ? (
                                <Check className="w-4 h-4 text-green-400" />
                              ) : (
                                <Copy className="w-4 h-4 text-slate-400" />
                              )}
                            </button>
                            <button className="p-2 hover:bg-slate-700/50 rounded-lg transition-colors" title="Good response">
                              <ThumbsUp className="w-4 h-4 text-slate-400 hover:text-green-400" />
                            </button>
                            <button className="p-2 hover:bg-slate-700/50 rounded-lg transition-colors" title="Bad response">
                              <ThumbsDown className="w-4 h-4 text-slate-400 hover:text-red-400" />
                            </button>
                            <button className="p-2 hover:bg-slate-700/50 rounded-lg transition-colors" title="Regenerate">
                              <RefreshCw className="w-4 h-4 text-slate-400 hover:text-blue-400" />
                            </button>
                          </motion.div>
                        )}
                        
                        {message.sources && message.sources.length > 0 && (
                          <details className="mt-4 pt-4 border-t border-slate-700/50">
                            <summary className="cursor-pointer text-sm text-slate-400 hover:text-blue-400 flex items-center space-x-2 transition-colors">
                              <ChevronDown className="w-4 h-4" />
                              <span className="font-medium">{message.sources.length} source{message.sources.length > 1 ? 's' : ''}</span>
                            </summary>
                            <div className="mt-4 space-y-3">
                              {message.sources.map((source, idx) => (
                                <motion.div
                                  key={idx}
                                  initial={{ opacity: 0, x: -20 }}
                                  animate={{ opacity: 1, x: 0 }}
                                  transition={{ delay: idx * 0.1 }}
                                  className="p-4 rounded-xl bg-slate-900/50 border border-slate-700/50 hover:border-blue-500/30 transition-all duration-200"
                                >
                                  <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center space-x-2">
                                      <FileText className="w-4 h-4 text-blue-400" />
                                      <span className="text-sm font-medium text-slate-300">
                                        {source.title || `${source.source} - ${source.page}`}
                                      </span>
                                    </div>
                                    {source.relevance_score && (
                                      <span className="px-2 py-1 bg-green-500/10 border border-green-500/30 rounded-md text-xs font-medium text-green-400">
                                        {source.relevance_score}
                                      </span>
                                    )}
                                  </div>
                                  <p className="text-sm text-slate-400 leading-relaxed">{source.content}</p>
                                  {source.extraction_method && (
                                    <div className="mt-2 text-xs text-slate-600">
                                      Method: {source.extraction_method}
                                    </div>
                                  )}
                                </motion.div>
                              ))}
                            </div>
                          </details>
                        )}
                      </div>
                      
                      {message.role === 'user' && (
                        <div className="flex items-center justify-end space-x-2 mt-2">
                          <span className="text-xs text-slate-600">You</span>
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              
              {loading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex items-center space-x-3"
                >
                  <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center animate-pulse shadow-lg shadow-blue-500/30">
                    <Loader2 className="w-4 h-4 text-white animate-spin" />
                  </div>
                  <div className="flex space-x-1">
                    <motion.div
                      animate={{ y: [0, -8, 0] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                      className="w-2 h-2 bg-blue-500 rounded-full"
                    />
                    <motion.div
                      animate={{ y: [0, -8, 0] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                      className="w-2 h-2 bg-cyan-500 rounded-full"
                    />
                    <motion.div
                      animate={{ y: [0, -8, 0] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                      className="w-2 h-2 bg-blue-500 rounded-full"
                    />
                  </div>
                </motion.div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-slate-700/30 bg-gradient-to-t from-slate-900/40 to-slate-900/20 backdrop-blur-2xl p-6">
          <div className="max-w-4xl mx-auto">
            <div className="relative">
              <div className="flex items-end space-x-3">
                <div className="flex-1 relative">
                  <textarea
                    ref={inputRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask me anything..."
                    rows={1}
                    className="w-full px-6 py-4 border border-slate-700/50 rounded-2xl focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/30 text-slate-100 placeholder-slate-400 resize-none max-h-32 backdrop-blur-xl transition-all duration-300"
                    style={{
                      background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.4) 100%)',
                      minHeight: '56px'
                    }}
                    disabled={loading}
                  />
                  <div className="absolute right-4 bottom-4 flex items-center space-x-2">
                    <span className="text-xs text-slate-600">{input.length}</span>
                  </div>
                </div>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleSend}
                  disabled={loading || !input.trim()}
                  className="p-4 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 disabled:from-slate-700 disabled:to-slate-700 text-white rounded-2xl transition-all duration-300 disabled:cursor-not-allowed shadow-lg disabled:shadow-none"
                  style={{
                    boxShadow: loading || !input.trim() ? 'none' : '0 10px 40px rgba(59, 130, 246, 0.4)'
                  }}
                >
                  {loading ? (
                    <Loader2 className="w-6 h-6 animate-spin" />
                  ) : (
                    <Send className="w-6 h-6" />
                  )}
                </motion.button>
              </div>
            </div>
            
            <div className="flex items-center justify-between mt-4 px-2">
              <div className="flex items-center space-x-4 text-xs text-slate-600">
                <button 
                  onClick={clearChat}
                  className="hover:text-cyan-400 transition-colors flex items-center space-x-1 group"
                >
                  <Trash2 className="w-3 h-3 group-hover:text-cyan-400" />
                  <span>Clear chat</span>
                </button>
                <span>•</span>
                <span>Press Enter to send</span>
                <span>•</span>
                <span>Shift + Enter for new line</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-xs text-slate-600">Secure & Encrypted</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
