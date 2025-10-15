<template>
  <div class="space-y-6">
    <section class="card">
      <div class="card-header flex items-center justify-between">
        <h2>Filters</h2>
        <div class="flex gap-2">
          <button
            class="px-3 py-1.5 rounded-md bg-primary-600 text-white hover:bg-primary-700"
            :disabled="loading"
            @click="runAnalysis"
          >
            {{ loading ? 'Processing...' : 'Run Analysis' }}
          </button>
          <button
            class="px-3 py-1.5 rounded-md bg-gray-100 text-gray-700 hover:bg-gray-200"
            :disabled="loading"
            @click="loadVisualization"
          >
            Load Visualization
          </button>
        </div>
      </div>
      <div class="card-body grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-xs text-gray-500 mb-1">From</label>
          <input type="date" v-model="dateFrom" class="w-full border rounded-md px-2 py-1" />
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">To</label>
          <input type="date" v-model="dateTo" class="w-full border rounded-md px-2 py-1" />
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">Keyword</label>
          <input type="text" v-model="keyword" placeholder="e.g. AI, stocks" class="w-full border rounded-md px-2 py-1" />
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">Sources (comma separated)</label>
          <input type="text" v-model="sourcesInput" placeholder="cnn,bbc" class="w-full border rounded-md px-2 py-1" />
        </div>
      </div>
      <div v-if="error" class="px-4 pb-3 text-sm text-red-600">{{ error }}</div>
    </section>

    <section class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="card col-span-1">
        <div class="card-header">Sentiment Overview</div>
        <div class="card-body">
          <Doughnut v-if="sentimentChartData" :data="sentimentChartData" :options="sentimentOptions" />
          <div v-else class="text-sm text-gray-500">No data</div>
        </div>
      </div>

      <div class="card col-span-1">
        <div class="card-header">Keyword Frequency</div>
        <div class="card-body">
          <Bar v-if="keywordChartData" :data="keywordChartData" :options="barOptions" />
          <div v-else class="text-sm text-gray-500">No data</div>
        </div>
      </div>

      <div class="card col-span-1">
        <div class="card-header">Trending Topics</div>
        <div class="card-body">
          <Bar v-if="trendingChartData" :data="trendingChartData" :options="barOptions" />
          <div v-else class="text-sm text-gray-500">No data</div>
        </div>
      </div>
    </section>

    <section class="card">
      <div class="card-header flex items-center justify-between">
        <span>Articles ({{ totalArticles }})</span>
        <div class="text-xs text-gray-500">Page {{ currentPage }} of {{ totalPages }}</div>
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center py-8 text-gray-500">Loading...</div>
        <div v-else>
          <div class="overflow-x-auto">
            <table class="min-w-full text-sm">
              <thead class="bg-gray-50 text-gray-600">
                <tr>
                  <th class="px-3 py-2 text-left">#</th>
                  <th class="px-3 py-2 text-left">Title</th>
                  <th class="px-3 py-2 text-left">Author</th>
                  <th class="px-3 py-2 text-left">Source</th>
                  <th class="px-3 py-2 text-left">Published</th>
                  <th class="px-3 py-2 text-left">Sentiment</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(article, index) in paginatedArticles" :key="index" class="odd:bg-white even:bg-gray-50">
                  <td class="px-3 py-2">{{ index + 1 + (currentPage - 1) * itemsPerPage }}</td>
                  <td class="px-3 py-2 max-w-[28rem] truncate" :title="article.title">{{ article.title }}</td>
                  <td class="px-3 py-2">{{ article.author || '-' }}</td>
                  <td class="px-3 py-2">{{ article.source || article.source_name || '-' }}</td>
                  <td class="px-3 py-2">{{ formatDate(article.pub_date || article.published_at) }}</td>
                  <td class="px-3 py-2">
                    <span :class="['badge', sentimentBadgeClass(article.label || article.sentiment)]">
                      {{ feedbackText(article.label || article.sentiment) }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="flex justify-center items-center gap-3 mt-4">
            <button @click="prevPage" :disabled="currentPage === 1" class="px-3 py-1.5 rounded-md bg-gray-100 disabled:opacity-50">Previous</button>
            <button @click="nextPage" :disabled="currentPage === totalPages" class="px-3 py-1.5 rounded-md bg-gray-100 disabled:opacity-50">Next</button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { Doughnut, Bar } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
} from 'chart.js';
import dayjs from 'dayjs';
import { useNewsStore } from '../stores/useNewsStore';

ChartJS.register(Title, Tooltip, Legend, ArcElement, BarElement, CategoryScale, LinearScale);

export default {
  name: 'DashBoard',
  components: { Doughnut, Bar },
  data() {
    return {
      currentPage: 1,
      itemsPerPage: 10,
      // local filter inputs (mirrors store)
      dateFrom: '',
      dateTo: '',
      keyword: '',
      sourcesInput: '',
    };
  },
  computed: {
    store() {
      return useNewsStore();
    },
    loading() {
      return this.store.loading;
    },
    error() {
      return this.store.error;
    },
    totalArticles() {
      return this.store.totalArticles;
    },
    articles() {
      return this.store.articles;
    },
    sentiments() {
      return this.store.sentiments;
    },
    keywordFrequency() {
      return this.store.keywordFrequency;
    },
    trendingTopics() {
      return this.store.trendingTopics;
    },
    totalPages() {
      return Math.max(1, Math.ceil(this.articles.length / this.itemsPerPage));
    },
    paginatedArticles() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.articles.slice(start, end);
    },
    sentimentChartData() {
      if (!this.sentiments) return null;
      const positive = this.sentiments.positive || 0;
      const neutral = this.sentiments.neutral || 0;
      const negative = this.sentiments.negative || 0;
      return {
        labels: ['Positive', 'Neutral', 'Negative'],
        datasets: [
          {
            data: [positive, neutral, negative],
            backgroundColor: ['#22c55e', '#a3a3a3', '#ef4444'],
          },
        ],
      };
    },
    sentimentOptions() {
      return {
        plugins: { legend: { position: 'bottom' } },
      };
    },
    keywordChartData() {
      if (!this.keywordFrequency?.length) return null;
      const labels = this.keywordFrequency.map((k) => k.keyword || k.term);
      const data = this.keywordFrequency.map((k) => k.count || k.frequency || 0);
      return {
        labels,
        datasets: [
          {
            label: 'Frequency',
            backgroundColor: '#6366f1',
            data,
          },
        ],
      };
    },
    trendingChartData() {
      if (!this.trendingTopics?.length) return null;
      const labels = this.trendingTopics.map((t) => t.topic || t.term);
      const data = this.trendingTopics.map((t) => t.score || t.count || 0);
      return {
        labels,
        datasets: [
          {
            label: 'Trend Score',
            backgroundColor: '#10b981',
            data,
          },
        ],
      };
    },
    barOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: '#6b7280' } },
          y: { ticks: { color: '#6b7280' } },
        },
      };
    },
  },
  mounted() {
    // initialize local filters from store
    this.dateFrom = this.store.dateFrom;
    this.dateTo = this.store.dateTo;
    this.keyword = this.store.keyword;
    this.sourcesInput = (this.store.sources || []).join(',');
    // attempt to load visualization on first mount
    this.loadVisualization();
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '-';
      const d = dayjs(dateString);
      return d.isValid() ? d.format('DD MMM YYYY') : '-';
    },
    sentimentBadgeClass(label) {
      if (label === -1 || label === 'negative') return 'bg-red-100 text-red-700';
      if (label === 1 || label === 'positive') return 'bg-green-100 text-green-700';
      return 'bg-gray-100 text-gray-700';
    },
    applyFiltersToStore() {
      const sources = this.sourcesInput
        ? this.sourcesInput.split(',').map((s) => s.trim()).filter(Boolean)
        : [];
      this.store.setFilters({
        dateFrom: this.dateFrom,
        dateTo: this.dateTo,
        keyword: this.keyword,
        sources,
      });
    },
    async runAnalysis() {
      this.applyFiltersToStore();
      try {
        await this.store.fetchAndAnalyze();
        this.currentPage = 1;
      } catch (e) {
        // error handled in store
      }
    },
    async loadVisualization() {
      this.applyFiltersToStore();
      try {
        await this.store.fetchVisualization();
        this.currentPage = 1;
      } catch (e) {
        // error handled in store
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) this.currentPage += 1;
    },
    prevPage() {
      if (this.currentPage > 1) this.currentPage -= 1;
    },
  },
};
</script>

<style scoped>
.card-body :deep(canvas) {
  /* Ensure charts adapt to container height */
  max-height: 280px;
}
</style>
