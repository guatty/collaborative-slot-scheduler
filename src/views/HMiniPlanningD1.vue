<template>
  <div class="home">
    <MiniPlanningD1 />
  </div>
</template>

<script>
// @ is an alias to /src
import MiniPlanningD1 from "@/components/MiniPlanningD1.vue";

export default {
  name: "Home",
  components: {
    MiniPlanningD1,
  },
  mounted(){
      if(!this.$store.getters["auth/isAuthenticatedEvenIfExpired"]){
          this.$router.push("/D1/planningGlobal");
      }
  }
};
</script>

<style>
</style>