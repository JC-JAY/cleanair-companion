import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'ca-alerts',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CommonModule, MatCardModule, MatIconModule, TranslateModule],
  template: `
    <div class="alerts-container">
      <mat-card>
        <mat-card-header>
          <mat-icon mat-card-avatar color="primary">notifications</mat-icon>
          <mat-card-title>{{ 'nav.alerts' | translate }}</mat-card-title>
          <mat-card-subtitle>AQI Threshold &amp; Best-Window Reminders</mat-card-subtitle>
        </mat-card-header>
        <mat-card-content>
          <p>Configure Web Push, WhatsApp, or SMS alerts when AQI crosses your threshold.</p>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`.alerts-container { max-width: 640px; margin: 0 auto; }`],
})
export class AlertsComponent {}

