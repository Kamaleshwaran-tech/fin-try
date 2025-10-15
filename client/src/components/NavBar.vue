<template>
  <header class="bg-white/70 backdrop-blur sticky top-0 z-30 shadow-sm">
    <div class="container-responsive flex items-center justify-between py-3">
      <div class="flex items-center gap-2">
        <img src="/favicon.ico" class="h-6 w-6" alt="logo" />
        <span class="font-semibold text-gray-800">News Sentiment Dashboard</span>
      </div>
      <nav class="flex items-center gap-4 text-sm text-gray-600">
        <a href="#" class="hover:text-primary-600 transition">Overview</a>
        <a href="#" class="hover:text-primary-600 transition">Articles</a>
        <a href="#" class="hover:text-primary-600 transition">Trends</a>
      </nav>
    </div>
  </header>
</template>

<script>
export default {
  name: 'NavBar',
};
</script>

<style scoped>
</style>
