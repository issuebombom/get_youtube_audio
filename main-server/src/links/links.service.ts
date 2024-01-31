import { HttpService } from '@nestjs/axios';
import { Injectable, InternalServerErrorException } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { lastValueFrom } from 'rxjs';
import { Link } from './schemas/links.schema';
import { Model } from 'mongoose';

@Injectable()
export class LinksService {
  constructor(
    private httpService: HttpService,
    @InjectModel(Link.name) private linkModel: Model<Link>,
  ) {}

  async createLinksInformation({ sendLinksMessageDto }) {
    try {
      const res = await lastValueFrom(
        this.httpService.post(
          'http://extractor-server:5000/links',
          sendLinksMessageDto,
        ),
      );
      const data = res.data;
      return data;
    } catch (err) {
      throw new InternalServerErrorException(err.response?.data ?? err);
    }
  }
}
