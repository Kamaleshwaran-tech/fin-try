// Pinia store to manage news articles, sentiments, and filters
import { defineStore } from 'pinia';
import dayjs from 'dayjs';
import api from '../services/api';

export const useNewsStore = defineStore('news', {
  state: () => ({
    articles: [],
    sentiments: null, // { positive: n, neutral: n, negative: n }
    keywordFrequency: [], // [{ keyword, count }]
    trendingTopics: [], // [{ topic, score }]
    loading: false,
    error: null,
    // Filters
    dateFrom: dayjs().subtract(7, 'day').format('YYYY-MM-DD'),
    dateTo: dayjs().format('YYYY-MM-DD'),
    sources: [],
    keyword: '',
    // Sources list from backend (optional)
    availableSources: [],
  }),
  getters: {
    totalArticles(state) {
      return state.articles?.length || 0;
    },
  },
  actions: {
    setError(message) {
      this.error = message;
    },
    setLoading(value) {
      this.loading = value;
    },
    setFilters({ dateFrom, dateTo, sources, keyword }) {
      if (dateFrom !== undefined) this.dateFrom = dateFrom;
      if (dateTo !== undefined) this.dateTo = dateTo;
      if (sources !== undefined) this.sources = sources;
      if (keyword !== undefined) this.keyword = keyword;
    },

    async fetchAndAnalyze() {
      this.setLoading(true);
      this.setError(null);
      try {
        const basePayload = {
          date_from: this.dateFrom,
          date_to: this.dateTo,
          sources: this.sources,
          keyword: this.keyword,
        };
        // Step 1: Extract articles
        await api.extract(basePayload);
        // Step 2: Analyze sentiments
        const analyzeRes = await api.analyze(basePayload);
        const data = analyzeRes?.data || {};
        this.articles = data.articles || [];
        this.sentiments = data.sentiments || null;
        this.keywordFrequency = data.keyword_frequency || [];
        this.trendingTopics = data.trending_topics || [];
        return data;
      } catch (err) {
        this.setError(err.message || 'Failed to analyze data');
        throw err;
      } finally {
        this.setLoading(false);
      }
    },

    async fetchVisualization() {
      this.setLoading(true);
      this.setError(null);
      try {
        const params = {
          date_from: this.dateFrom,
          date_to: this.dateTo,
          sources: this.sources,
          keyword: this.keyword,
        };
        const res = await api.visualize(params);
        const data = res?.data || {};
        // Accept same fields if provided via /visualize
        if (data.articles) this.articles = data.articles;
        if (data.sentiments) this.sentiments = data.sentiments;
        if (data.keyword_frequency) this.keywordFrequency = data.keyword_frequency;
        if (data.trending_topics) this.trendingTopics = data.trending_topics;
        return data;
      } catch (err) {
        this.setError(err.message || 'Failed to load visualization data');
        throw err;
      } finally {
        this.setLoading(false);
      }
    },
  },
});
