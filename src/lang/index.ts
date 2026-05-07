import zhCN from './zh-CN';
import enUS from './en-US';
import { moment } from 'obsidian';

export type Lang = typeof enUS;

export default {
  'en-US': enUS,
  'zh-CN': zhCN,
  get current() {
    const langIds = ['en-US', 'zh-CN'];
    const locale = moment.locale().toLowerCase();
    let langId = langIds.find(id => id.toLowerCase() === locale.toLowerCase());
    if (langId) {
      return this[langId as 'en-US' | 'zh-CN'];
    }

    const localePrefix = locale.split('-')[0];
    langId = langIds.find(id => id.toLowerCase().startsWith(localePrefix));
    if (langId) {
      return this[langId as 'en-US' | 'zh-CN'];
    }
    return this['en-US'];
  },
};
