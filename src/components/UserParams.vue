<template>
  <br/>
</template>

<script>
import axios from "axios";
export default {
  components: {
  },
  props: {
    chosen_params: Object
  },
  data() {
    return {
      loading: false,
      h_wusers: {},
      ishwuloaded: false,
    };
  },
  watch: {
    h: [
      {
        handler: "geth_wuser",
      },
    ],
  },
  methods: {
    geth_wuser(el) {
      this.ishwuloaded = false;
      const body = JSON.stringify({
        class_id: el.class_id,
      });
      /* TODO : 
            await Http.request({
        method: "POST",
        url: this.$API_URL + "/confirmCancelCreneauPlanning",
        headers: {
          Authorization: `Bearer: ${this.$store.getters["auth/getJWT"]}`,
          "Access-Control-Allow-Origin": "*",
          "Content-Type": "application/json",
        },
        data: body,
      })
        .then(() => {
          */
      axios
        .post(this.$API_URL + "/classInfo", body, {
          headers: {
            Authorization: `Bearer: ${this.$store.getters["auth/getJWT"]}`,
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
          },
        })
        .then((response) => {
          console.log(response.data);
          this.h_wusers = response.data;
          this.ishwuloaded = true;
        });
    },
    register() {
      this.loading = true;

      var user_self_inscript_id = 2;
      // const requestOptions = {
      //   method: "POST",
      //   headers: { "Content-Type": "application/json" },
      //   body: JSON.stringify({
      //     user_assigned: user_self_inscript_id,
      //     user_modif: user_self_inscript_id,
      //     reason: "Self-inscript",
      //     timestamp_start: this.ts.s_begin,
      //     timestamp_end: this.ts.s_end,
      //     class_id: this.h.class_id,
      //     timeslot_kind: this.kind,
      //   }),
      // };
      // fetch(this.$API_URL + "/registerRoneoD1", requestOptions)
      //   .then((response) => response.json())
      //   // .then((data) => console.log(data))
      //   .then(() => {
      //     this.$refs.modalName.close();
      //     this.$emit("refresh");
      //   });
      const body = {
        user_assigned: user_self_inscript_id,
        user_modif: user_self_inscript_id,
        reason: "Self-inscript",
        timestamp_start: this.ts.s_begin,
        timestamp_end: this.ts.s_end,
        class_id: this.h.class_id,
        timeslot_kind: this.kind,
      };
      axios
        .post(this.$API_URL + "/registerRoneoD1", body, {
          headers: {
            Authorization: `Bearer: ${this.$store.getters["auth/getJWT"]}`,
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
          },
        })
        .then(() => {
          this.loading = false;
          this.$emit("refresh");
          this.$refs.modalName.close();
        });
    },
  },
};
</script>

<style>
</style>