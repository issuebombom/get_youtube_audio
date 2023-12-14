import { Body, Controller, Get } from '@nestjs/common';
import { GetLinksInformationDto } from './dto/get-links-information.dto';
import { LinksService } from './links.service';
import { HttpService } from '@nestjs/axios';
import { catchError, map } from 'rxjs';

@Controller('links')
export class LinksController {
  constructor(
    private linksService: LinksService,
    private httpService: HttpService,
  ) {}

  @Get('/get-url-info')
  getLinksInformation(@Body() getLinksInformationDto: GetLinksInformationDto) {
    const res = this.httpService
      .post('http://127.0.0.1:5000/urls', getLinksInformationDto)
      .pipe(map((res) => res.data))
      .pipe(
        catchError((error) => {
          throw new Error(error);
        }),
      );
    return res;
  }
}
