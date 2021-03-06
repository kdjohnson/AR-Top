import { Vector3 } from 'three'

/**
 * Class used to define static utility functions for a map object.
 *
 * @export
 * @class MapUtils
 */
export class MapUtils {
  /**
   * This function returns a boolean of whether the specified position is
   * within the bounds of the specified map.
   *
   * @param {Map} map
   * @param {Vector3} position
   *
   * @returns {boolean}
   *
   * @memberOf MapUtils
   */
  static isPositionWithinBounds (map, position) {
    // Ensure the the map is defined
    if (!map) throw new Error('Map must be defined.')

    return ((position.x >= 0 && position.x < map.width) &&
      (position.y >= 0 && position.y < map.height) &&
      (position.z >= 0 && position.z < map.depth))
  }

  /**
   * This function converts a unit position to an actual position on the
   * specified map.
   *
   * @static
   * @param {Map} map
   * @param {Vector3} actualPosition
   * @returns {Vector3}
   *
   * @memberOf MapUtils
   */
  static convertActualToUnitPosition (map, actualPosition) {
    // Ensure the the map is defined
    if (!map) throw new Error('Map must be defined.')

    let offset = new Vector3(map.getActualWidth() / 2, 0, map.getActualDepth() / 2)
    return actualPosition
      .clone()
      .add(offset)
      .divideScalar(map.unitSize)
      .floor()
      .multiplyScalar(map.unitSize)
      .divideScalar(map.unitSize)
  }

  /**
   * This function converts an actual position to a unit position on the
   * specified map.
   *
   * @static
   * @param {Map} map
   * @param {Vector3} unitPosition
   * @returns {Vector3}
   *
   * @memberOf MapUtils
   */
  static convertUnitToActualPosition (map, unitPosition) {
    // Ensure that the map is defined
    if (!map) throw new Error('Map must be defined.')

    let offset = new Vector3(map.getActualWidth() / 2, 0, map.getActualDepth() / 2)
    return unitPosition
      .clone()
      .multiplyScalar(map.unitSize)
      .addScalar(map.unitSize / 2)
      .sub(offset)
  }

  /**
   * Serialize a map object into relevant json data.
   *
   * @static
   * @param {Map} map
   * @returns serialized map json
   *
   * @memberOf MapUtils
   */
  static serialize (map) {
    let space = 2
    let ignoredFields = [
      'object',
      'scene',
      'unitSize',
      'actualSize',
      'actualHeight',
      'scale',
      '_listeners']
    return JSON.stringify(map, (key, value) => {
      return ignoredFields.includes(key) ? undefined : value
    }, space)
  }
}
