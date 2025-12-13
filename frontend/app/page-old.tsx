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
  Plus
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import axios from 'axios'

interface Message {
  role: 'user' | 'assistant'
  content: string
  source_type?: 'knowledge_base' | 'general_knowledge'
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

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [initializing, setInitializing] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)
  const [hoveredMessage, setHoveredMessage] = useState<number | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Load chat history from localStorage
    const savedMessages = localStorage.getItem('chat_history')
    if (savedMessages) {
      try {
        setMessages(JSON.parse(savedMessages))
      } catch (e) {
        console.error('Failed to load chat history:', e)
      }
    }
    // Auto-initialize on mount
    initializeAssistant()
  }, [])

  useEffect(() => {
    // Save chat history to localStorage whenever messages change
    if (messages.length > 0) {
      localStorage.setItem('chat_history', JSON.stringify(messages))
    }
  }, [messages])

  const initializeAssistant = async () => {
    try {
      await axios.post('http://localhost:8000/api/initialize')
      // Focus input after initialization
      setTimeout(() => inputRef.current?.focus(), 100)
    } catch (error) {
      console.error('Failed to initialize:', error)
      // Retry after a moment
      setTimeout(initializeAssistant, 3000)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = { role: 'user', content: input }
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
        sources: response.data.sources
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Failed to send message:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleClear = () => {
    if (confirm('Clear all conversation history?')) {
      setMessages([])
      localStorage.removeItem('chat_history')
      axios.post('http://localhost:8000/api/clear').catch(console.error)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="h-screen bg-gray-900 flex">
      {/* Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ x: -300 }}
            animate={{ x: 0 }}
            exit={{ x: -300 }}
            className="fixed inset-y-0 left-0 z-50 w-72 bg-gray-950 border-r border-gray-800 flex flex-col"
          >
            <div className="p-4 border-b border-gray-800 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">Chat History</h2>
              <button onClick={() => setSidebarOpen(false)} className="text-gray-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="flex-1 p-4 overflow-y-auto">
              <div className="space-y-2">
                {messages.filter(m => m.role === 'user').slice(-10).map((msg, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-gray-800 hover:bg-gray-700 rounded-lg cursor-pointer text-sm text-gray-300 truncate"
                    onClick={() => {
                      const msgIndex = messages.findIndex(m => m === msg)
                      if (msgIndex >= 0) {
                        const targetMsg = document.getElementById(`msg-${msgIndex}`)
                        targetMsg?.scrollIntoView({ behavior: 'smooth' })
                      }
                    }}
                  >
                    {msg.content}
                  </div>
                ))}
                {messages.length === 0 && (
                  <div className="text-gray-500 text-sm text-center py-8">
                    No chat history yet
                  </div>
                )}
              </div>
            </div>

            <div className="p-4 border-t border-gray-800 space-y-2">
              <button
                  onClick={handleClear}
                  disabled={messages.length === 0}
                  className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-red-600 hover:bg-red-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg text-white transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>Clear all history</span>
                </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-gray-950 border-b border-gray-800 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="flex items-center space-x-2">
              <BookOpen className="w-5 h-5 text-gray-400" />
              <span className="font-semibold text-white">Personal Knowledge Assistant</span>
            </div>
          </div>
          
          <div className="flex items-center space-x-2 text-sm text-gray-400">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>Ready</span>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center p-8">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center max-w-2xl"
              >
                <div className="mb-6">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-gray-500 to-gray-600 mb-4">
                    <Sparkles className="w-8 h-8 text-white" />
                  </div>
                </div>
                <h2 className="text-3xl font-bold text-white mb-3">
                  How can I help you today?
                </h2>
                <p className="text-gray-400 mb-8">
                  Ask me anything about your documents or any general question
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-8">
                  {[
                    { q: "What is a data warehouse?", icon: BookOpen },
                    { q: "Explain the process models", icon: FileText },
                    { q: "What is Python?", icon: Sparkles },
                    { q: "Summarize the fundamentals", icon: Brain }
                  ].map((example, idx) => (
                    <motion.button
                      key={idx}
                      onClick={() => setInput(example.q)}
                      className="flex items-center space-x-3 p-4 bg-gray-800 hover:bg-gray-750 rounded-xl text-left transition-colors border border-gray-700 hover:border-gray-600"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <example.icon className="w-5 h-5 text-gray-400 flex-shrink-0" />
                      <span className="text-sm text-gray-300">{example.q}</span>
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto w-full px-4 py-8">
              <AnimatePresence>
                {messages.map((message, index) => (
                  <motion.div
                    key={index}
                    id={`msg-${index}`}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-8"
                  >
                    <div className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-[80%] ${message.role === 'user' ? 'order-2' : 'order-1'}`}>
                        {message.role === 'assistant' && (
                          <div className="flex items-center space-x-2 mb-2">
                            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-gray-500 to-gray-600 flex items-center justify-center">
                              <Sparkles className="w-3 h-3 text-white" />
                            </div>
                            <span className="text-xs text-gray-500">Assistant</span>
                          </div>
                        )}
                        
                        <div
                          className={`rounded-2xl px-4 py-3 ${
                            message.role === 'user'
                              ? 'bg-gray-600 text-white ml-auto'
                              : 'bg-gray-800 text-gray-100'
                          }`}
                        >
                          <ReactMarkdown className="prose prose-sm prose-invert max-w-none">
                            {message.content}
                          </ReactMarkdown>
                          
                          {message.source_type && (
                            <div className="mt-2 pt-2 border-t border-gray-700">
                              {message.source_type === 'knowledge_base' ? (
                                <span className="inline-flex items-center space-x-1 text-xs text-blue-400">
                                  <BookOpen className="w-3 h-3" />
                                  <span>From your documents</span>
                                </span>
                              ) : (
                                <span className="inline-flex items-center space-x-1 text-xs text-purple-400">
                                  <Sparkles className="w-3 h-3" />
                                  <span>General knowledge</span>
                                </span>
                              )}
                            </div>
                          )}

                          {message.sources && message.sources.length > 0 && (
                            <details className="mt-3">
                              <summary className="cursor-pointer text-xs text-gray-400 hover:text-gray-300 flex items-center space-x-1">
                                <ChevronDown className="w-3 h-3" />
                                <span>View {message.sources.length} source{message.sources.length > 1 ? 's' : ''}</span>
                              </summary>
                              <div className="mt-3 space-y-3">
                                {message.sources.map((source, idx) => (
                                  <div key={idx} className="bg-gray-900 p-3 rounded-lg border border-gray-800">
                                    <div className="flex items-center justify-between mb-2">
                                      <div className="font-semibold text-gray-300 text-xs">
                                        {source.title || `${source.source} - Page ${source.page}`}
                                      </div>
                                      {source.relevance_score && (
                                        <span className="text-xs px-2 py-0.5 bg-gray-800 text-green-400 rounded">
                                          {source.relevance_score}
                                        </span>
                                      )}
                                    </div>
                                    {source.page && !source.title && (
                                      <div className="text-xs text-gray-500 mb-2">
                                        {source.page} • {source.extraction_method || 'PDF'}
                                      </div>
                                    )}
                                    <div className="text-xs text-gray-400 leading-relaxed">
                                      {source.content}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </details>
                          )}
                        </div>
                        
                        {message.role === 'user' && (
                          <div className="flex items-center justify-end space-x-2 mt-2">
                            <span className="text-xs text-gray-500">You</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              
              {loading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex items-center space-x-2 text-gray-400"
                >
                  <div className="w-6 h-6 rounded-full bg-gradient-to-br from-gray-500 to-gray-600 flex items-center justify-center">
                    <Loader2 className="w-3 h-3 text-white animate-spin" />
                  </div>
                  <span className="text-sm">Thinking...</span>
                </motion.div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-gray-800 bg-gray-950 p-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-end space-x-2">
              <div className="flex-1 relative">
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Send a message..."
                  className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-white placeholder-gray-500 pr-12"
                  disabled={loading}
                />
              </div>
              <button
                onClick={handleSend}
                disabled={loading || !input.trim()}
                className="bg-gray-600 hover:bg-gray-700 text-white p-3 rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
              >
                {loading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
            <div className="text-xs text-gray-500 text-center mt-2">
              Ask anything about your documents or general questions
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
