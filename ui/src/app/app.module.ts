import { APP_INITIALIZER, NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { HttpClientModule } from "@angular/common/http";
import { AppRoutingModule } from "./app-routing.module";
import { AppComponent } from "./app.component";
import { MarketPlaceComponent } from "@/components/marketplace/marketplace.component";
import { SharedStoreService } from "@/services/shared-store.service";
import { LogStreamViewerComponent } from "./components/log-stream-viewer/log-stream-viewer.component";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { MonacoEditorModule } from "ngx-monaco-editor-v2";
import { ConfigEditorComponent } from "./components/config-editor/config-editor.component";
import { PrimeNgModule } from "./modules/primeng.module";
import { DatabaseInfoComponent } from "./components/database-info/database-info.component";
import { CustomPackageManagerComponent } from "./components/custom-package-manager/custom-package-manager.component";
import { PackageDetailsViewerComponent } from "./components/package-details-viewer/package-details-viewer.component";
import { ShoppingCartComponent } from "./components/shopping-cart/shopping-cart.component";
import { MagicMirrorControllerComponent } from "./components/magicmirror-controller/magicmirror-controller.component";
import { MirrorPreviewComponent } from "./components/mirror-preview/mirror-preview.component";
import { CurrentlyInstalledComponent } from "./components/currently-installed/currently-installed.component";
import { DoctorComponent } from "./components/doctor/doctor.component";
import { providePrimeNG } from "primeng/config";
import Aura from "@primeuix/themes/aura";
import { definePreset } from "@primeuix/themes";
import { DragScrollDirective } from "./directives/drag-scroll.directive";

// Design tokens matching styles.scss oklch palette
const MMPMPreset = definePreset(Aura, {
  components: {
    toast: {
      colorScheme: {
        dark: {
          root: { blur: '0' },
          info: {
            background:   'oklch(0.72 0.07 200 / 0.12)',
            borderColor:  'oklch(0.72 0.07 200 / 0.35)',
            color:        'oklch(0.72 0.07 200)',
            detailColor:  'oklch(0.90 0.006 80)',
            shadow:       '0 8px 24px oklch(0 0 0 / 0.40)',
            closeButton:  { hoverBackground: 'oklch(0.72 0.07 200 / 0.12)' },
          },
          success: {
            background:   'oklch(0.78 0.12 160 / 0.12)',
            borderColor:  'oklch(0.78 0.12 160 / 0.35)',
            color:        'oklch(0.78 0.12 160)',
            detailColor:  'oklch(0.90 0.006 80)',
            shadow:       '0 8px 24px oklch(0 0 0 / 0.40)',
            closeButton:  { hoverBackground: 'oklch(0.78 0.12 160 / 0.12)' },
          },
          warn: {
            background:   'oklch(0.83 0.11 75 / 0.12)',
            borderColor:  'oklch(0.83 0.11 75 / 0.35)',
            color:        'oklch(0.83 0.11 75)',
            detailColor:  'oklch(0.90 0.006 80)',
            shadow:       '0 8px 24px oklch(0 0 0 / 0.40)',
            closeButton:  { hoverBackground: 'oklch(0.83 0.11 75 / 0.12)' },
          },
          error: {
            background:   'oklch(0.68 0.14 22 / 0.12)',
            borderColor:  'oklch(0.68 0.14 22 / 0.35)',
            color:        'oklch(0.68 0.14 22)',
            detailColor:  'oklch(0.90 0.006 80)',
            shadow:       '0 8px 24px oklch(0 0 0 / 0.40)',
            closeButton:  { hoverBackground: 'oklch(0.68 0.14 22 / 0.12)' },
          },
        },
      },
    },
  },
});

export function init_shared_store(store: SharedStoreService) {
  return () => store.load();
}

@NgModule({
  declarations: [
    AppComponent,
    DragScrollDirective,
    MarketPlaceComponent,
    LogStreamViewerComponent,
    ConfigEditorComponent,
    DatabaseInfoComponent,
    CustomPackageManagerComponent,
    PackageDetailsViewerComponent,
    ShoppingCartComponent,
    MagicMirrorControllerComponent,
    MirrorPreviewComponent,
    CurrentlyInstalledComponent,
    DoctorComponent,
  ],
  imports: [BrowserAnimationsModule, BrowserModule, AppRoutingModule, HttpClientModule, PrimeNgModule, MonacoEditorModule.forRoot()],
  providers: [
    {
      provide: APP_INITIALIZER,
      useFactory: init_shared_store,
      deps: [SharedStoreService],
      multi: true,
    },
    providePrimeNG({
      theme: {
        preset: MMPMPreset,
        options: {
          darkModeSelector: ':root',
        },
      },
    }),
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}
