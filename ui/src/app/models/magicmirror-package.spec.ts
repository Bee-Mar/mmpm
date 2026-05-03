import { MagicMirrorPackage } from './magicmirror-package';

describe('MagicMirrorPackage', () => {
  it('can construct a valid package object', () => {
    const pkg: MagicMirrorPackage = {
      title: 'MMM-Test',
      author: 'tester',
      repository: 'https://github.com/tester/MMM-Test',
      description: 'A test module',
      directory: 'MMM-Test',
      category: 'Test',
      is_installed: false,
      is_upgradable: false,
      remote_details: null as any,
      stars: 0,
      last_updated: '2024-01-01',
    };

    expect(pkg.title).toBe('MMM-Test');
    expect(pkg.is_installed).toBeFalse();
    expect(pkg.is_upgradable).toBeFalse();
  });

  it('supports optional license field', () => {
    const pkg: MagicMirrorPackage = {
      title: 'MMM-Licensed',
      author: 'author',
      repository: 'https://github.com/author/MMM-Licensed',
      description: 'desc',
      directory: 'MMM-Licensed',
      category: 'Other',
      is_installed: true,
      is_upgradable: false,
      remote_details: null as any,
      stars: 10,
      last_updated: '2024-06-01',
      license: 'MIT',
    };

    expect(pkg.license).toBe('MIT');
  });
});
