<template>
  <footer class="mt-10 border-t border-gray-100">
    <div class="container-responsive py-6 text-sm text-gray-500 flex items-center justify-between">
      <span>© {{ new Date().getFullYear() }} News Analytics</span>
      <span>Built with Vue 3, Pinia, Tailwind, Chart.js</span>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'AppFooter',
};
</script>

<style scoped>
</style>
