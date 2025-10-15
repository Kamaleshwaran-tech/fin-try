<template>
  <div id="app" class="min-h-screen bg-gray-50 text-gray-800">
    <NavBar />
    <main class="container-responsive py-6">
      <transition name="fade" mode="out-in">
        <DashBoard />
      </transition>
    </main>
    <AppFooter />
  </div>
  
</template>

<script>
import DashBoard from './components/DashBoard.vue';
import NavBar from './components/NavBar.vue';
import AppFooter from './components/AppFooter.vue';

export default {
  name: 'App',
  components: {
    NavBar,
    DashBoard,
    AppFooter,
  },
};
</script>

<style>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
