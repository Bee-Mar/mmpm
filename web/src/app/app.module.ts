import {APP_INITIALIZER, NgModule} from '@angular/core';
import {BrowserModule} from '@angular/platform-browser';
import {HttpClientModule} from "@angular/common/http";
import {AppRoutingModule} from './app-routing.module';
import {AppComponent} from './app.component';
import {MagicMirrorDatabaseComponent} from '@/magicmirror/components/magicmirror-database/magicmirror-database.component';
import {SharedStoreService} from '@/services/shared-store.service';
import {MagicMirrorPackageAPI} from '@/services/api/magicmirror-package-api.service';

export function init_shared_store(store: SharedStoreService) {
  return () => store.retrieve_packages();
}

@NgModule({
  declarations: [
    AppComponent,
    MagicMirrorDatabaseComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
  ],
  providers: [
    MagicMirrorPackageAPI,
    SharedStoreService,
    {
      provide: APP_INITIALIZER,
      useFactory: init_shared_store,
      deps: [SharedStoreService],
      multi: true,
    },

  ],
  bootstrap: [AppComponent]
})
export class AppModule {}
