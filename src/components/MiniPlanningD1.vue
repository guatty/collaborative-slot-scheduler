<template>
  <Planning :horaires="horaires"  
    @refresh="refreshPlanning"
    v-bind="$attrs"
  />
</template>

<script>
import Planning from "./Planning.vue";
import { Http } from "@capacitor-community/http";
export default {
  components: { Planning },
  data() {
    return { horaires: [] };
  },
  mounted() {
    this.refreshPlanning();
  },
  methods: {
    async refreshPlanning() {
      this.horaires = [];
      await Http.request({
        method: "GET",
        url: this.$API_URL + "/rollingPlanningD1",
      })
        .then(({ data }) => {
          this.horaires = data;
        })
        .catch((err) => console.log(err));
    },
  },
};
</script>

<style>
</style>