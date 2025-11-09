import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi'

const lightTheme = {
  dark: false,
  colors: {
    background: '#FFFFFF',
    surface: '#F9FBF9',
    'surface-variant': '#E8F5E9',
    'on-surface-variant': '#424242',
    primary: '#00C853',
    'primary-darken-1': '#009624',
    secondary: '#424242',
    'secondary-darken-1': '#212121',
    accent: '#69f0ae',
    error: '#B00020',
    info: '#2196F3',
    success: '#4CAF50',
    warning: '#FB8C00',
  },
}

const darkTheme = {
  dark: true,
  colors: {
    background: '#0a0f0d',
    surface: '#121917',
    'surface-variant': '#1a2421',
    'on-surface-variant': '#c2cdc7',
    primary: '#00c853',
    'primary-darken-1': '#00a043',
    secondary: '#1de9b6',
    'secondary-darken-1': '#00bfa5',
    accent: '#69f0ae',
    error: '#ef5350',
    info: '#29b6f6',
    success: '#00c853',
    warning: '#ffa726',
  },
}

const vuetify = createVuetify({
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: 'darkTheme',
    themes: {
      lightTheme,
      darkTheme,
    },
  },
  defaults: {
    VCard: {
      elevation: 2,
    },
    VBtn: {
      elevation: 1,
    },
    VAppBar: {
      elevation: 1,
    },
  },
})

export default vuetify