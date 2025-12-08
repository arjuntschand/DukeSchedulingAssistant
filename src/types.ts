export type ChatRole = 'user' | 'assistant' | 'system';

export interface SourceChunk {
  text: string;
  source_file?: string;
  page?: number;
  chunk_index?: number;
  type?: string;
}

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  timestamp: string; // ISO string
  retrievedChunks?: string[];
  sources?: SourceChunk[];
  fewshotChunks?: string[];
}

export interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: string; // ISO string
}

export interface PrattProfile {
  major: string;
  classYear: string;
  semester: string;
  currentCourses: string[];
  completedCourses: string[];
}
