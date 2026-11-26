// AQI badge — shared header component showing current AQI with CPCB colour
import { Component, OnInit, inject, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { AqiService } from '../../../core/services/aqi.service';
import { ProfileService } from '../../../core/services/profile.service';

@Component({
  selector: 'ca-aqi-badge',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CommonModule, MatChipsModule, MatTooltipModule],
  template: `
    <ng-container *ngIf="aqi$ | async as aqi">
      <span class="aqi-badge" 
            [style.background-color]="getColor(aqi.aqi)"
            [style.color]="getTextColor(aqi.aqi)"
            [matTooltip]="'AQI ' + aqi.aqi + ' — ' + (aqi.aqi_category || 'N/A') + ' | PM2.5: ' + aqi.pm25 + ' µg/m³'"
            role="status"
            [attr.aria-label]="'Air Quality Index: ' + aqi.aqi">
        AQI {{ aqi.aqi ?? '—' }}
        <span class="cache-dot" *ngIf="aqi.from_cache" title="Cached data">●</span>
      </span>
    </ng-container>
    <span *ngIf="!(aqi$ | async)" class="aqi-badge aqi-unavailable">AQI —</span>
  `,
  styles: [`
    .aqi-badge {
      display: inline-flex; align-items: center; gap: 4px;
      padding: 4px 12px; border-radius: 16px;
      font-weight: 700; font-size: 14px; cursor: help;
    }
    .aqi-unavailable { background: #9e9e9e; color: white; }
    .cache-dot { font-size: 8px; opacity: 0.7; }
  `]
})
export class AqiBadgeComponent implements OnInit {
  private aqiSvc = inject(AqiService);
  private profileSvc = inject(ProfileService);
  readonly aqi$ = this.aqiSvc.aqi$;

  ngOnInit() {
    const profile = this.profileSvc.current;
    if (profile?.latitude && profile?.longitude) {
      this.aqiSvc.fetchAQI(profile.latitude, profile.longitude).subscribe();
    } else {
      // Default: Pune
      this.aqiSvc.fetchAQI(18.52, 73.85).subscribe();
    }
  }

  getColor(aqi: number | null): string { return AqiService.aqiColor(aqi); }
  getTextColor(aqi: number | null): string {
    if (!aqi || aqi <= 100) return '#1a1a1a';
    return '#ffffff';
  }
}

