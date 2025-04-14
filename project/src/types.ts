export interface Article {
  title: string;
  url: string;
  date: string;
  content: string;
  source: string;
}

export interface NewsResponse {
  topic: string;
  articles: Article[];
  summary: string;
  status: 'completed' | 'failed';
}