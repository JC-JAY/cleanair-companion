import { Component, inject, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatButtonModule } from '@angular/material/button';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'ca-settings',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonToggleModule,
    MatSlideToggleModule,
    MatButtonModule,
    TranslateModule,
  ],
  template: `
    <div class="settings-container">
      <mat-card>
        <mat-card-header>
          <mat-card-title>{{ 'nav.settings' | translate }}</mat-card-title>
        </mat-card-header>
        <mat-card-content class="settings-body">
          <div>
            <h4>Language</h4>
            <mat-button-toggle-group [value]="currentLang" (change)="setLang($event.value)">
              <mat-button-toggle value="en">English</mat-button-toggle>
              <mat-button-toggle value="hi">हिन्दी</mat-button-toggle>
              <mat-button-toggle value="mr">मराठी</mat-button-toggle>
            </mat-button-toggle-group>
          </div>

          <mat-slide-toggle [checked]="largeText" (change)="toggleLargeText($event.checked)">
            Large text mode (Accessibility)
          </mat-slide-toggle>

          <div>
            <button mat-stroked-button color="warn" (click)="deleteAccount()">
              Delete my data &amp; account
            </button>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .settings-container { max-width: 640px; margin: 0 auto; }
    .settings-body { display: flex; flex-direction: column; gap: 20px; padding-top: 12px; }
  `],
})
export class SettingsComponent {
  private translate = inject(TranslateService);
  private auth = inject(AuthService);

  currentLang = localStorage.getItem('lang') || 'en';
  largeText = localStorage.getItem('largeText') === 'true';

  setLang(lang: string) {
    this.currentLang = lang;
    localStorage.setItem('lang', lang);
    this.translate.use(lang);
  }

  toggleLargeText(enabled: boolean) {
    this.largeText = enabled;
    localStorage.setItem('largeText', String(enabled));
    document.body.classList.toggle('large-text', enabled);
  }

  deleteAccount() {
    this.auth.deleteAccount().subscribe();
  }
}

