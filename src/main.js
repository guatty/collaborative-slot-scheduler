import {
	createApp
} from 'vue'
import App from './App.vue'
import './registerServiceWorker'
import router from './router'
import store from './store'
import moment from 'moment'
import 'moment/locale/fr'
moment.locale('fr')

const app = createApp(App);
app.use(router).use(store).mount('#app');

app.config.globalProperties.$moment = moment;
app.config.globalProperties.$tsHm = (ts) => moment.utc(ts * 1000).format('HH[h]mm');
app.config.globalProperties.$API_URL = process.env.VUE_APP_APIURL === undefined ? "https://www.apecs.ml" : process.env.VUE_APP_APIURL;

app.config.globalProperties.$filters = {
	date_to_fr(value) {
		return moment(String(value)).format('dddd Do MMMM YYYY')
	}
}
