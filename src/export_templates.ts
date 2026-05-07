import type { ExportSetting } from './settings';

export default {
  'Word (.docx)': {
    name: 'Word (.docx)',
    type: 'pandoc',
    arguments: '',
    optionsMeta: {
      'referenceDocx': 'preset:referenceDocx',
    },
    extension: '.docx',
  },
} satisfies Record<string, ExportSetting> as Record<string, ExportSetting>;
