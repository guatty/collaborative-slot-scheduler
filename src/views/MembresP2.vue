<template>
  <div class="home">
    <h3>Liste des membres inscrits en P2</h3>
    <h4 v-if="hasNoData">
      Vous n'avez pas le droit de consulter les données personnelles des
      membres.
    </h4>
    <template v-else>
      <!-- <label for="hideinactive">Cacher les membres non actifs (erasmus, démission, ...)</label> -->
      <input type="checkbox" id="hideinactive" v-model="hideinactive">
      <table-lite
        :has-checkbox="true"
        :is-loading="table.isLoading"
        :is-re-search="table.isReSearch"
        :columns="table.columns"
        :rows="membersP2"
        :total="membersP2.length"
        @do-search="doSearch"
        @is-finished="tableLoadingFinish"
        @return-checked-rows="updateCheckedRows"
      ></table-lite>
    </template>
  </div>
</template>

<script>
import TableLite from "vue3-table-lite";
import { Http } from "@capacitor-community/http";
export default {
  name: "MembresP2",
  components: { TableLite },
  data() {
    return {
      sortable: true,
      membersP2: [],
      hideinactive: true,
      hasNoData: false,
      table: {
        messages: {
          pagingInfo: "{0}-{1} sur {2}",
          pageSizeChangeLabel: "Nombre de membres :",
          gotoPageLabel: "Page :",
          noDataAvailable: "Chargement en cours...",
        },
        isLoading: false,
        isReSearch: false,
        columns: [
          {
            label: "Prénom",
            field: "firstname",
            width: "9%",
            sortable: true,
            display: function (row) {
              return row.firstname;
            },
          },
          {
            label: "Nom",
            field: "lastname",
            width: "9%",
            sortable: true,
            display: function (row) {
              return row.lastname;
            },
          },
          {
            label: "Contribution P2",
            field: "contribution_p2",
            width: "9%",
            sortable: true,
            display: function (row) {
              if (row.cat == null) {
                return '<p style="color:red;">Ne s\'est pas encore inscrit·e sur le planning.</p>';
              } else if (
                row.cat["h_scribe"] >= 2 && row.cat["h_proofread"] >= 2
              ) {
                return '<p style="color:green;">A pris ses heures ! (S'+row.cat["h_scribe"]+'R'+row.cat["h_proofread"]+') </p>';
              } else {
                return '<p style="color:red;">N\'a pas pris suffisamment d\'heures. (S'+row.cat["h_scribe"]+'R'+row.cat["h_proofread"]+') </p>';
              }
            },
          },
          {
            label: "Mail",
            field: "mail",
            width: "9%",
            sortable: true,
            display: function (row) {
              return row.mail;
            },
          },
          {
            label: "Facebook",
            field: "facebook",
            width: "9%",
            sortable: true,
            display: function () {
              return "Non renseigné";
            },
          },
          {
            label: "Discord",
            field: "discord",
            width: "9%",
            sortable: true,
            display: function () {
              return "Non renseigné";
            },
          },
          {
            label: "Promo",
            field: "school_year",
            width: "9%",
            sortable: true,
            display: function (row) {
              return row.school_year;
            },
          },
          {
            label: "Droits",
            field: "right_group",
            width: "9%",
            sortable: true,
            display: function (row) {
              return row.right_group;
            },
          },
          {
            label: "Inscription",
            field: "active_kind",
            width: "9%",
            sortable: true,
            display: function (row) {
              return row.active_kind;
            },
          },
          {
            label: "",
            field: "notifications",
            width: "9%",
            sortable: true,
            display: function () {
              return "Mail: Désactivées. Application: Désactivées.";
            },
          },
          // {
          //   label: "ID",
          //   field: "id",
          //   width: "3%",
          //   sortable: true,
          //   isKey: true,
          // },
          // {
          //   label: "Name",
          //   field: "name",
          //   width: "10%",
          //   sortable: true,
          //   display: function (row) {
          //     return (
          //       '<a href="#" data-id="' + row.user_id + '" class="name-btn">' + row.name + "</button>"
          //     );
          //   },
          // },
          // {
          //   label: "Email",
          //   field: "email",
          //   width: "15%",
          //   sortable: true,
          // },
          // {
          //   label: "",
          //   field: "quick",
          //   width: "10%",
          //   display: function (row) {
          //     return (
          //       '<button type="button" data-id="' + row.user_id + '" class="quick-btn">Button</button>'
          //     );
          //   },
          // },
        ],
        rows: [
          {
            id: 1,
            name: "TEST1",
          },
        ],
      },
    };
  },
  computed: {
    loggedIn() {
      return this.$store.getters["auth/isAuthenticated"];
    },
  },
  created() {
    if (!this.loggedIn) {
      this.$router.push({ name: "LoginP2" });
    }
  },
  mounted() {
    this.refreshMembers();
  },
  watch: {
    hideinactive: function() { this.refreshMembers(); }
  },
  methods: {
    logout() {
      this.$store.dispatch("auth/logout");
      this.$router.push({ name: "LoginP2" });
    },
    async refreshMembers() {
      this.membersP2 = [];

      await Http.request({
        method: "POST",
        url: this.$API_URL + "/membersP2",
        headers: {
          Authorization: `Bearer: ${this.$store.getters["auth/getJWT"]}`,
          "Access-Control-Allow-Origin": "*",
          "Content-Type": "application/json",
        },
        data: {"hideinactive" : this.hideinactive}
      })
        .then(({ data }) => {
          if (data.length) {
            this.membersP2 = data;
          } else {
            this.hasNoData = true;
          }
        })
        .catch((err) => {
          console.log(err);
          this.hasNoData = true;
        });
    },
  },
};
</script>
<style>
table td {
  padding: 0 !important;
  vertical-align: middle !important;
}
</style>