<template>
    <div class="hello">
      <h1>{{ message }}</h1>
    </div>
  </template>
  
  <script>
  export default {
    name: 'HelloWorld',
    data() {
      return {
        message: 'Hello, Vue!'
      };
    }
  }
  </script>
  
  <style scoped>
  .hello {
    text-align: center;
    font-family: Arial, sans-serif;
    color: #2c3e50;
    margin-top: 40px;
  }
  </style>
  