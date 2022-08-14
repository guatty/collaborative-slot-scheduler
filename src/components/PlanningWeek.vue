<script>
import WeekDay from "./WeekDay.vue";
export default {
  components: { WeekDay },
  props: { week: Array },
  data: () => ({
    collapsed: false,
  }),
  methods: {
    toggleCollapsed() {
      this.collapsed = !this.collapsed;
    },
  },
};
</script>

<template>
  <br />
  <div class="weekHeader" @click="toggleCollapsed()">
    📅 Semaine {{ week.week_number }} <span v-if="collapsed" style="margin-left: 15px; font-weight: bolder;"> ( {{ week.week_days.length }} jours cachés )</span>
  </div>
  <div class="weekDays" v-show="!this.collapsed">
    <div
      class="weekDay"
      v-for="weekDay in week.week_days"
      :key="weekDay.h_date"
    >
      <WeekDay
        v-bind:weekDay="weekDay"
        @showModal="showModal"
        @showModalConfirmDelete="showModalConfirmDelete"
		v-bind="$attrs" 
      />
    </div>
  </div>
</template>

<style>
</style>