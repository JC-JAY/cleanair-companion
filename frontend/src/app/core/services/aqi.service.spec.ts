import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { AqiService } from './aqi.service';

describe('AqiService', () => {
  let service: AqiService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [AqiService],
    });
    service = TestBed.inject(AqiService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should return correct color for AQI values', () => {
    expect(AqiService.aqiColor(30)).toBe('#55a84f');  // Good
    expect(AqiService.aqiColor(75)).toBe('#a3c853');  // Satisfactory
    expect(AqiService.aqiColor(150)).toBe('#fbc02d'); // Moderate
    expect(AqiService.aqiColor(250)).toBe('#f29c33'); // Poor
    expect(AqiService.aqiColor(350)).toBe('#e93f33'); // Very Poor
    expect(AqiService.aqiColor(450)).toBe('#af2d24'); // Severe
    expect(AqiService.aqiColor(null)).toBe('#9e9e9e');
  });

  it('should have initial default AQI data', () => {
    const aqi = service.currentAQI;
    expect(aqi).toBeTruthy();
    expect(aqi.lat).toBe(18.52);
    expect(aqi.lon).toBe(73.85);
  });
});
