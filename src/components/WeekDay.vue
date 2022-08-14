<script>
import ClassCard from "./ClassCard.vue";
export default {
  components: { ClassCard },
  props: { weekDay: Array },
  data: () => ({
    activeItem: Object,
    visible: true,
    collapsed: false,
  }),
  mounted() {
    for (let h_class in this.weekDay.day_hclasses) {
      this.activeItem[h_class.class_id] = "flex";
    }
  },
  methods: {
    toggleCollapsed() {
      this.collapsed = !this.collapsed;
    },
    toggleActiveCategorie(cat) {
      let i = 0;
      for (let h_class in this.weekDay.day_hclasses) {
        if (h_class.categorie == cat) {
          this.activeItem[h_class.class_id] = "none";
          i++;
        }
      }
      this.visible = i < this.weekDay.length;
    },
  },
};
</script>

<template>
  <div class="hdate" v-show="visible" @click="toggleCollapsed()">
    {{ $filters.date_to_fr(weekDay.h_date) }} <span v-if="collapsed" style="margin-left: 15px; font-weight: bolder;"> ( {{ weekDay.day_hclasses.length }} cours cachés )</span>
  </div>
  <div class="classesOfTheDay" v-show="visible && !collapsed">
    <ClassCard
      v-for="horaire in weekDay.day_hclasses"
      :key="horaire.class_id"
      v-bind:h="horaire"
      v-bind:style="{ display: activeItem[horaire.class_id] }"
      @showModal="showModal"
      @showModalConfirmDelete="showModalConfirmDelete"
      v-bind="$attrs" 
    />
  </div>
</template>

<style>
</style>