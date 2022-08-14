<template>
  <div class="home">
    <MiniPlanningP2 />
  </div>
</template>

<script>
// @ is an alias to /src
import MiniPlanningP2 from "@/components/MiniPlanningP2.vue";

export default {
  name: "Home",
  components: {
    MiniPlanningP2,
  },
  mounted(){
      if(!this.$store.getters["auth/isAuthenticatedEvenIfExpired"]){
          this.$router.push("/P2/planningGlobal");
      }
  }
};
</script>

<style>
</style>