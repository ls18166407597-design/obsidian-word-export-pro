import * as ct from 'electron';
import process from 'process';
import { PluginSettingTab } from 'obsidian';
import type { SemVer } from 'semver'
import type UniversalExportPlugin from '../main';
import { createSignal, createRoot, onCleanup, createMemo, createEffect, Show, JSX } from 'solid-js';
import { createStore, produce } from 'solid-js/store';
import { insert, Dynamic } from 'solid-js/web';
import type { Lang } from '../lang';
import {
  CustomExportSetting,
  ExportSetting,
  PandocExportSetting,
  createEnv,
} from '../settings';
import { setPlatformValue, getPlatformValue } from '../utils';
import pandoc from '../pandoc';
import Setting, { Text, Toggle, ExtraButton, DropDown } from './components/Setting';

const SettingTab = (props: { lang: Lang, plugin: UniversalExportPlugin }) => {
  const { plugin, lang } = props;
  const [settings, setSettingsStore] = createStore(plugin.settings);
  const [pandocVersion, setPandocVersion] = createSignal<SemVer>();
  const [modal] = createSignal<() => JSX.Element>();

  const setSettings = (...args: any[]) => {
    (setSettingsStore as any)(...args);
    plugin.saveSettings();
  };

  const currentCommandTemplate = createMemo(() => settings.items.find(v => v.name === settings.lastEditName) ?? settings.items[0]);
  const currentEditCommandTemplate = <T extends 'custom' | 'pandoc'>(type?: T) => {
    const template = currentCommandTemplate();
    return (type === undefined || type === template.type ? template : undefined) as T extends 'custom' ? CustomExportSetting : T extends 'pandoc' ? PandocExportSetting : ExportSetting;
  };
  const customDefaultExportDirectory = createMemo(() => getPlatformValue(settings.customDefaultExportDirectory));

  const updateCurrentEditCommandTemplate = (update: (prev: Partial<ExportSetting>) => void) => {
    const idx = settings.items.findIndex(v => v.name === settings.lastEditName);
    setSettings('items', idx === -1 ? 0 : idx, produce(item => {
      update(item);
      return item;
    }));
  };

  const pandocDescription = createMemo(() => {
    const version = pandocVersion();
    if (version) {
      if (app.vault.config.useMarkdownLinks && version.compare(pandoc.requiredVersion) === -1) {
        return lang.settingTab.pandocVersionWithWarning(pandoc.requiredVersion)
      }
      return lang.settingTab.pandocVersion(version)
    }
    return lang.settingTab.pandocNotFound;
  });

  const chooseCustomDefaultExportDirectory = async () => {
    const retval = await ct.remote.dialog.showOpenDialog({
      defaultPath: customDefaultExportDirectory() ?? ct.remote.app.getPath('documents'),
      properties: ['createDirectory', 'openDirectory'],
    });

    if (!retval.canceled && retval.filePaths.length > 0) {
      setSettings('customDefaultExportDirectory', v => setPlatformValue(v, retval.filePaths[0]));
    }
  };

  const choosePandocPath = async () => {
    const retval = await ct.remote.dialog.showOpenDialog({
      filters: process.platform == 'win32' ? [{ extensions: ['exe'], name: 'pandoc' }]: undefined,
      properties: ['openFile'],
    });

    if (!retval.canceled && retval.filePaths.length > 0) {
      setSettings('pandocPath', (v) => setPlatformValue(v, retval.filePaths[0]));
    }
  };

  createEffect(async () => {
    try {
      const env = createEnv(getPlatformValue(settings.env) ?? {});
      setPandocVersion(await pandoc.getVersion(getPlatformValue(settings.pandocPath), env));
    } catch {
      setPandocVersion(undefined);
    }
  });

  return <>
    <Setting name={lang.settingTab.general} heading={true} />

    <Setting name={lang.settingTab.pandocPath} description={pandocDescription()}>
      <Text
        placeholder={lang.settingTab.pandocPathPlaceholder}
        value={getPlatformValue(settings.pandocPath) ?? ''}
        onChange={(value) => setSettings('pandocPath', (v) => setPlatformValue(v, value))}
      />
      <ExtraButton icon="folder" onClick={choosePandocPath} />
    </Setting>

    <Setting name={lang.settingTab.defaultFolderForExportedFile}>
      <DropDown options={[
        { name: lang.settingTab.auto, value: 'Auto' },
        { name: lang.settingTab.sameFolderWithCurrentFile, value: 'Same' },
        { name: lang.settingTab.customLocation, value: 'Custom' }
      ]} selected={settings.defaultExportDirectoryMode} onChange={(v: 'Auto' | 'Same' | 'Custom') => setSettings('defaultExportDirectoryMode', v)} />
    </Setting>

    <Show when={settings.defaultExportDirectoryMode === 'Custom'}>
      <Setting>
        <Text value={customDefaultExportDirectory() ?? ''} title={customDefaultExportDirectory()} />
        <ExtraButton icon="folder" onClick={chooseCustomDefaultExportDirectory} />
      </Setting>
    </Show>

    <Setting name={lang.settingTab.openExportedFileLocation}>
      <Toggle
        checked={settings.openExportedFileLocation}
        onChange={(v) => setSettings('openExportedFileLocation', v)}
      />
    </Setting>

    <Setting name={lang.settingTab.openExportedFile} >
      <Toggle
        checked={settings.openExportedFile}
        onChange={(v) => setSettings('openExportedFile', v)} />
    </Setting>
    
    <Setting name={lang.settingTab.ShowExportProgressBar}>
      <Toggle
        checked={settings.showExportProgressBar}
        onChange={(v) => setSettings('showExportProgressBar', v)}
      />
    </Setting>



    <Show when={modal()}>
      <Dynamic component={modal()} ref={(el: Node) => document.body.appendChild(el)} />
    </Show>
  </>;
};

export default class extends PluginSettingTab {
  plugin: UniversalExportPlugin;
  #dispose?: () => void;

  public get lang() {
    return this.plugin.lang;
  }

  constructor(plugin: UniversalExportPlugin) {
    super(plugin.app, plugin);
    this.plugin = plugin;
    this.name = this.plugin.lang.settingTab.title;
  }

  display() {
    this.#dispose = createRoot(dispose => {
      insert(this.containerEl, <SettingTab plugin={this.plugin} lang={this.lang} />);
      onCleanup(() => {
        this.containerEl.empty();
      });
      return dispose;
    });
  }

  hide() {
    this.#dispose();
  }
}
