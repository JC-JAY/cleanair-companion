import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'ca-community',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CommonModule, MatCardModule, MatIconModule, TranslateModule],
  template: `
    <div class="community-container">
      <mat-card>
        <mat-card-header>
          <mat-icon mat-card-avatar color="primary">group</mat-icon>
          <mat-card-title>{{ 'nav.community' | translate }}</mat-card-title>
          <mat-card-subtitle>Neighbourhood &amp; School Clean-Air Groups</mat-card-subtitle>
        </mat-card-header>
        <mat-card-content>
          <p>Join local Pune/Mulshi groups to track collective CO₂e avoided and PM2.5 exposure saved.</p>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`.community-container { max-width: 800px; margin: 0 auto; }`],
})
export class CommunityComponent {}

