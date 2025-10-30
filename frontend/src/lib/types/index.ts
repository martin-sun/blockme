export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  loadedSkills?: string[];
}

export interface ChatRequest {
  message: string;
  conversationHistory?: Message[];
}

export interface ChatResponse {
  answer: string;
  loadedSkills: string[];
  tokensUsed?: number;
  routingInfo?: {
    confidence: 'low' | 'medium' | 'high';
    reasoning: string;
  };
}

export interface Document {
  id: string;
  filename: string;
  status: 'uploading' | 'processing' | 'completed' | 'failed';
  progress?: number;
  error?: string;
  skillId?: string;
}

export interface KnowledgeCollection {
  id: string;
  name: string;
  description: string;
  domain: string;
  documentCount: number;
  icon?: string;
}
