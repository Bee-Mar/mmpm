import { APP_INITIALIZER, NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { HttpClientModule } from "@angular/common/http";
import { AppRoutingModule } from "./app-routing.module";
import { AppComponent } from "./app.component";
import { MmpmMarketPlaceComponent } from "@/magicmirror/components/mmpm-marketplace/mmpm-marketplace.component";
import { SharedStoreService } from "@/services/shared-store.service";
import { TableModule } from "primeng/table";
import { DropdownModule } from "primeng/dropdown";
import { MultiSelectModule } from "primeng/multiselect";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { ButtonModule } from "primeng/button";
import { FormsModule } from "@angular/forms";
import { TabViewModule } from "primeng/tabview";
import { DialogModule } from "primeng/dialog";
import { ProgressSpinnerModule } from "primeng/progressspinner";
import { PanelModule } from "primeng/panel";
import { ToolbarModule } from "primeng/toolbar";
import { OverlayPanelModule } from "primeng/overlaypanel";
import { DividerModule } from "primeng/divider";
import { ScrollerModule } from "primeng/scroller";
import { TooltipModule } from "primeng/tooltip";

export function init_shared_store(store: SharedStoreService) {
  return () => store.get_packages();
}

@NgModule({
  declarations: [AppComponent, MmpmMarketPlaceComponent],
  imports: [
    BrowserAnimationsModule,
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    TableModule,
    DropdownModule,
    MultiSelectModule,
    ButtonModule,
    FormsModule,
    TabViewModule,
    DialogModule,
    ProgressSpinnerModule,
    PanelModule,
    ToolbarModule,
    OverlayPanelModule,
    DividerModule,
    ScrollerModule,
    TooltipModule,
  ],
  providers: [
    {
      provide: APP_INITIALIZER,
      useFactory: init_shared_store,
      deps: [SharedStoreService],
      multi: true,
    },
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}
